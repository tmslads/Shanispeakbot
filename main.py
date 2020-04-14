import itertools
import logging
import pickle
import pprint
import random as r
import re
import sqlite3
from datetime import datetime, date
from time import sleep, time as cur_time

import chatterbot
import emoji
from telegram.ext import (CommandHandler, ConversationHandler, InlineQueryHandler, MessageHandler, Filters,
                          PicklePersistence, Updater, CallbackQueryHandler, PollAnswerHandler)
from textblob import TextBlob

import chatbot
import inline
from quiz import send_quiz, receive_answer
from commands import BotCommands as bc, prohibited
from constants import group_ids, testbot
from convos import (bday, magic, nick, settings_gui, start)
from convos.namer import nicknamer
from online import gcalendar

logging.basicConfig(format='%(asctime)s - %(name)s - %(levelname)s - %(message)s', level=logging.INFO)

with open("files/token.txt", 'r') as file:
    shanisir_token, test_token = file.read().split(',')

chatbot.shanisirbot.initialize()  # Does any work that needs to be done before the chatbot can process responses.

pp = PicklePersistence(filename='files/user_data')
updater = Updater(token=f'{test_token}', use_context=True, persistence=pp)

dp = updater.dispatcher
shanisir_bot = updater.bot
get_tags = chatbot.shanisirbot.storage.tagger.get_bigram_pair_string


last_reacted_at = 0
bot_response = None

rebukes = ["this is not the expected behaviour", "i don't want you to talk like that",
           "this language is embarrassingassing to me like basically", "this is not a fruitful conversation"]

r.shuffle(rebukes)
rebukes = itertools.cycle(rebukes)


def connection(query: str, update=None, fetchall=False):
    """Connect to database and execute given query."""

    conn = sqlite3.connect('./files/bot_settings.db')
    c = conn.cursor()

    if update is not None:
        chat_id = update.effective_chat.id
        c.execute(f"SELECT EXISTS(SELECT * FROM CHAT_SETTINGS WHERE chat_id = {chat_id});")
        result = c.fetchone()

        if not result[0]:  # If /settings was never called
            name = update.effective_chat.title
            if name is None:  # Will be None when it is a private chat
                name = update.effective_chat.first_name

            c.execute(f"INSERT INTO CHAT_SETTINGS VALUES({chat_id},'{name}','❌',0.3,0.2);")  # First time use
            conn.commit()

    c.execute(query)

    if fetchall:
        result = c.fetchall()
        conn.close()
        return result
    else:
        result = c.fetchone()
        conn.close()
        return result[0]


def media(update, context):
    """Sends a reaction to media messages (pictures, videos, documents, voice notes)"""

    global last_reacted_at

    now = cur_time()

    if now - last_reacted_at < 60:  # If a reaction was sent less than a minute ago
        return  # Don't send a reaction

    last_reacted_at = cur_time()

    chat_id = update.effective_chat.id
    msg = update.message.message_id

    true = connection(f"SELECT MEDIA_PROB FROM CHAT_SETTINGS WHERE CHAT_ID={chat_id};", update)
    false = 1 - true

    try:
        doc = update.message.document.file_name[-3:]
    except AttributeError:  # When there is no document sent
        doc = ''
    name = nicknamer(update, context)

    img_reactions = ["😂", "🤣", "😐", f"Not funny {name} okay?", "This is not fine like you say", "*giggles*",
                     f"This is embarrassing to me {name}", "What your doing?! Go for the worksheet"]

    vid_reactions = ["😂", "🤣", "😐", f"I've never seen anything like this {name}", "What is this",
                     "Now I feel very bad like", f"Are you fine {name}?"]

    voice_reactions = ["What is this", f"I can't hear you {name}", f"Are you fine {name}?",
                       "Now your on the track like", "Your voice is funny like you say",
                       f"See I can't tolerate this {name}", "What your saying??"]

    app_reactions = ["Is this a virus", "I'm just suggesting like, don't open this", "We just don't mind that okay?"]

    prob = r.choices([0, 1], weights=[false, true])[0]  # Probabilities are 0.7 - False, 0.3 - True by default
    if prob:
        shanisir_bot.send_chat_action(chat_id=chat_id, action='typing')
        sleep(2)

        if update.message.photo:
            print("Img")
            shanisir_bot.send_message(chat_id=chat_id, text=r.choice(img_reactions), reply_to_message_id=msg)

        elif update.message.voice:
            print("voiceee")
            shanisir_bot.send_message(chat_id=chat_id, text=r.choice(voice_reactions), reply_to_message_id=msg)

        elif update.message.video or doc == 'mp4' or doc == 'gif':
            print("vid")
            shanisir_bot.send_message(chat_id=chat_id, text=r.choice(vid_reactions), reply_to_message_id=msg)

        elif doc == 'apk' or doc == 'exe':
            print("app")
            shanisir_bot.send_message(chat_id=chat_id, text=r.choice(app_reactions), reply_to_message_id=msg)


def del_pin(update, context):
    """Deletes pinned message service status from the bot."""
    context.bot.delete_message(chat_id=update.effective_chat.id, message_id=update.message.message_id)


def reply(update, context):
    if update.message.reply_to_message.from_user.username == testbot.replace('@', ''):  # If the reply is from a bot:
        private(update, context, grp=True, the_id=update.message.message_id)  # send a response like in private chat


def group(update, context):
    """Checks for profanity in messages and responds to that."""

    chat_id = update.effective_chat.id
    if any(bad_word in update.message.text.lower().split() for bad_word in prohibited):
        true = connection(f"SELECT PROFANE_PROB FROM CHAT_SETTINGS WHERE CHAT_ID={chat_id};", update)
        false = 1 - true

        if r.choices([0, 1], weights=[false, true])[0]:  # Probabilities are 0.8 - False, 0.2 - True by default.
            name = nicknamer(update, context)

            out = f"{next(rebukes)} {name}"
            shanisir_bot.send_message(chat_id=chat_id, text=out,
                                      reply_to_message_id=update.message.message_id)  # Sends message
            print(f"Rebuke: {out}")


def private(update, context, grp=False, the_id=None, isgrp="(PRIVATE)"):
    global bot_response

    user = update.message.from_user
    msg_text = update.message.text
    chat_id = update.effective_chat.id

    JJ_RB = ["like you say", "like you speak"]  # For Adjectives or Adverbs

    # Checks if your username or fullname or chat id is present in our records. If not, adds them.
    if 'username' not in context.user_data:
        context.user_data['username'] = [user.username]

    elif user.username != context.user_data['username'][-1]:
        context.user_data['username'].append(user.username)

    if 'full_name' not in context.user_data:
        context.user_data['full_name'] = [user.full_name]

    elif user.full_name != context.user_data['full_name'][-1]:
        context.user_data['full_name'].append(user.full_name)

    if "chat_ids" not in context.chat_data:
        context.chat_data["chat_ids"] = [chat_id]

    elif chat_id not in context.chat_data['chat_ids']:  # Gets chat id of the user in which they have talked to the bot
        context.chat_data['chat_ids'].append(chat_id)

    # Attempted fix-
    pp.update_user_data(update.effective_user.id, context.user_data)
    pp.update_chat_data(chat_id, context.chat_data)

    if testbot in msg_text:  # Sends response if bot is @'ed in group
        msg_text = re.sub(r"(\s*)@Ttessttingbot(\s*)", ' ', msg_text)  # Remove mention from text so response is better
        the_id = update.message.message_id
        grp = True

    if bot_response is None:
        search_in_response_text = None
    else:
        search_in_response_text = get_tags(bot_response.text)

    # If the user's message is a reply to a message
    if update.message.reply_to_message is not None:
        reply_text = update.message.reply_to_message.text

        bot_response = chatterbot.conversation.Statement(text=reply_text, search_text=get_tags(reply_text))
        user_msg = chatterbot.conversation.Statement(text=msg_text,
                                                     search_text=get_tags(msg_text),
                                                     in_response_to=bot_response,
                                                     search_in_response_to=get_tags(reply_text))
    else:
        user_msg = chatterbot.conversation.Statement(text=msg_text,
                                                     search_text=get_tags(msg_text),
                                                     in_response_to=bot_response,
                                                     search_in_response_to=search_in_response_text)

    reply = f"(REPLY TO [{user_msg.in_response_to}])"

    if grp:
        isgrp = f"(GROUP: {update.effective_chat.title})"
    else:  # Learn user's latest message (user_msg) as response to bot's last message (bot_response)
        chatbot.shanisirbot.learn_response(user_msg, bot_response)

    bot_response = chatbot.shanisirbot.get_response(user_msg.text)
    try:
        bot_msg = bot_response.text
    except AttributeError:
        bot_msg = 'Hello'

    punctuation = r"""!"#$%&'()*+,-./:;<=>?@[\]^_`{|}~"""
    bot_msg = ''.join(c for c in bot_msg if c not in punctuation)
    blob = TextBlob(bot_msg)
    cleaned = blob.words  # Returns list with no punctuation marks

    flag = 0  # To check if a modal is present in the sentence
    lydcount = 0  # Counts the number of times "like you do" has been added
    JJ_RBcount = 0  # Counts the number of times a phrase from JJ_RB has been added

    if len(cleaned) < 20:
        lydlim = 1  # to limit the number of times we add
        JJ_RBlim = 1  # lyd and JJ_RB
    else:
        lydlim = len(cleaned) // 20
        JJ_RBlim = len(cleaned) // 20

    temp = 0

    for word, tag in blob.tags:  # returns list of tuples which tells the POS
        index = cleaned.index(word)
        if index - temp < 7:  # Do not add lad things too close to each other
            continue

        if tag == 'MD' and not flag:  # Modal
            cleaned.insert(index + 1, "(if the laws of physics allow it)")
            flag = 1

        if tag in ['JJ', 'JJR', 'JJS', 'RB', 'RBR', 'RBS'] and JJ_RBcount < JJ_RBlim:  # Adjective or Adverb
            cleaned.insert(index + 1, r.choice(JJ_RB))
            JJ_RBcount += 1
            temp = index

        elif tag in ['VB', 'VBD', 'VBG', 'VBN', 'VBP', 'VBZ'] and lydcount < lydlim:  # Verb
            cleaned.insert(index + 1, "like you do")
            lydcount += 1
            temp = index

    name = nicknamer(update, context)

    if r.choice([0, 1]):
        if r.choice([0, 1]):
            cleaned.append(r.choice(["I am so sowry", "i don't want to talk like that",
                                     "it is embarrassing to me like basically", "it's not to trouble you like you say",
                                     "go for the worksheet", "it's not that hard"]))
        else:
            cleaned.append(r.choice(["it will be fruitful", "you will benefit", "that is the expected behaviour",
                                     "now you are on the track like", "now class is in the flow like",
                                     "aim to hit the tarjit", "don't press the jockey"]))
        cleaned.insert(0, name)
    else:
        cleaned.append(name)

    if len(cleaned) < 5:  # Will run if input is too short
        cleaned.append(r.choice(["*draws perfect circle*", "*scratches nose*"]))

    if re.search('when|time', ' '.join(cleaned), flags=re.IGNORECASE):
        cleaned.insert(-1, 'decide a date')

    for word in update.message.text:
        if word in emoji.UNICODE_EMOJI:  # Checks if emoji is present in message
            cleaned.append(r.choice(list(emoji.UNICODE_EMOJI)))  # Adds a random emoji

    shanitext = ' '.join(cleaned).capitalize()

    with open("files/interactions.txt", "a") as f1:
        inp = f"UTC+0 {update.message.date} {isgrp} {reply} {update.message.from_user.full_name}" \
              f" ({update.message.from_user.username}) SAID: {update.message.text}\n"
        out = shanitext

        print(f"{inp}\n{out}")

        f1.write(emoji.demojize(inp))
        f1.write(f"BOT REPLY: {emoji.demojize(out)}\n\n")

        shanisir_bot.send_chat_action(chat_id=chat_id, action='typing')  # Sends 'typing...' status for 6 sec
        # Assuming 25 WPM typing speed on a phone
        time_taken = (25 / 60) * len(out.split())
        sleep(time_taken) if time_taken < 6 else sleep(6)  # Sends status for 6 seconds if message is too long to type
        shanisir_bot.send_message(chat_id=chat_id, text=out, reply_to_message_id=the_id)  # Sends message


def morning_goodness(context):
    """Send a "good morning" quote to the groups, along with a clip"""

    right_now = datetime.now()  # returns: Datetime obj

    if 'last_sent' not in context.bot_data:
        context.bot_data['last_sent'] = right_now

    diff = right_now - context.bot_data['last_sent']

    # Send only if it has been over a day since last good morning message-
    if diff.days < 1:
        return

    with open("files/good_mourning.txt", "r") as greetings:
        position = context.bot_data['seek']
        if position == 13642:  # If EOF was reached
            position = 0  # Start from the beginning
        greetings.seek(position)

        greeting = greetings.readline()
        print(greeting)
        context.bot_data['seek'] = greetings.tell()

    ids = connection("SELECT CHAT_ID FROM CHAT_SETTINGS WHERE MORNING_MSGS='✅';", fetchall=True)

    # Bug with ptb where performer,title,thumb might be ignored when a url is supplied in 'audio' param in 'send_audio'.
    # Workaround for now is to just open mp3 from desktop-

    clip_loc = r"C:/Users/Uncle Sam/Desktop/sthyaVERAT/4 FUN ya Practice/Shanisirmodule/Assets/clips/good mourning.mp3"

    for chat_id in ids:
        try:
            msg = shanisir_bot.send_message(chat_id=chat_id[0], text=greeting)
            shanisir_bot.pin_chat_message(chat_id=chat_id[0], message_id=msg.message_id, disable_notification=True)
            shanisir_bot.send_chat_action(chat_id=chat_id[0], action='upload_audio')
            shanisir_bot.send_audio(chat_id=chat_id[0], title="Good morning", performer="Shani sir",
                                    audio=open(clip_loc, "rb"), thumb=open("files/shanisir.jpeg", 'rb'))

        except Exception as e:  # When chat is private, no rights to pin message, or if bot was removed.
            print(e)

    context.bot_data['last_sent'] = datetime(right_now.year, right_now.month, right_now.day, 8)  # Set it as 8AM today
    pp.update_bot_data(context.bot_data)  # Have to update this manually as ptb 12.5 has new bug


def bday_wish(context):
    """Wishes you on your birthday."""

    gcalendar.main()
    days_remaining, name = gcalendar.get_next_bday()

    # Wishes from Google Calendar-
    if days_remaining == 0:
        msg = context.bot.send_message(chat_id=group_ids['12b'],
                                       text=f"Happy birthday {name}! May the mass times acceleration be with you!🎉"
                                            f"What your going to do today like?")

        shanisir_bot.pin_chat_message(chat_id=group_ids['12b'], message_id=msg.message_id, disable_notification=True)

        now = str(date.today())
        today = datetime.strptime(now, "%Y-%m-%d")  # Parses today's date (time object) into datetime object
        new_date = today.replace(year=today.year + 1)

        gcalendar.CalendarEventManager(name=name).update_event(new_date)  # Updates bday to next year

    # TODO: Wishes from /tell birthday input-


def prettyprintview():
    with open('files/user_data', 'rb') as f:
        pprint.PrettyPrinter(indent=2).pprint(pickle.load(f))


dp.add_handler(InlineQueryHandler(inline.inline_clips))
dp.add_handler(CommandHandler(command='help', callback=bc.helper))
dp.add_handler(CommandHandler(command='secret', callback=bc.secret))
dp.add_handler(CommandHandler(command='start', callback=bc.start))
dp.add_handler(CommandHandler(command='swear', callback=bc.swear))
dp.add_handler(CommandHandler(command='snake', callback=bc.snake))
dp.add_handler(CommandHandler(command='facts', callback=bc.facts))
dp.add_handler(CommandHandler(command='quizizz', callback=bc.quizizz))
dp.add_handler(CommandHandler(command='test', callback=send_quiz))  # TODO: This should be a job
dp.add_handler(PollAnswerHandler(callback=receive_answer))


# /8ball conversation-
magicball_handler = ConversationHandler(
    entry_points=[
        CommandHandler(command="8ball", callback=magic.magic8ball, filters=~Filters.reply),
        MessageHandler(filters=Filters.command(False) & Filters.regex("8ball") & Filters.reply,
                       callback=magic.thinking)
                  ],

    states={
        magic.PROCESSING: [MessageHandler(filters=Filters.reply & Filters.text, callback=magic.thinking)]
    },

    fallbacks=[CommandHandler(command='cancel', callback=magic.cancel)
               ],
    conversation_timeout=20
)
dp.add_handler(magicball_handler)

# /tell conversation
# TODO: Add deep-linked parameter to pc for people calling /tell in groups.
tell_handler = ConversationHandler(
    entry_points=[CommandHandler('tell', start.initiate, filters=Filters.private)],

    states={
        start.CHOICE: [MessageHandler(filters=Filters.regex("^Birthday$"), callback=bday.bday),
                       MessageHandler(filters=Filters.regex("^Nickname$"), callback=nick.nick),
                       MessageHandler(filters=Filters.regex("^Nothing$"), callback=start.leave)
                       ],
        bday.INPUT: [MessageHandler(filters=Filters.regex("^([1-9][0-9]{3}-[0-9]{2}-[0-9]{2})$"),  # Valid date check
                                    callback=bday.bday_add_or_update),
                     MessageHandler(filters=Filters.text, callback=bday.wrong)  # If it is not a date
                     ],

        bday.MODIFY: [MessageHandler(filters=Filters.regex("^Forget my birthday sir$"), callback=bday.bday_del),

                      MessageHandler(filters=Filters.regex("^Update my birthday sir$"), callback=bday.bday_mod)
                      ],

        nick.SET_NICK: [MessageHandler(filters=Filters.text & Filters.reply, callback=nick.add_edit_nick)],

        nick.MODIFY_NICK: [MessageHandler(filters=Filters.regex("^Change nickname$"), callback=nick.edit_nick),
                           MessageHandler(filters=Filters.regex("^Remove nickname$"), callback=nick.del_nick),
                           MessageHandler(filters=Filters.regex("^Back$"), callback=nick.back)
                           ],

        ConversationHandler.TIMEOUT: [MessageHandler(filters=Filters.all, callback=start.timedout)]
        },
    fallbacks=[MessageHandler(Filters.regex("^No, thank you sir$"), callback=bday.reject),
               CommandHandler("cancel", start.leave)
               ],

    name="/tell convo", persistent=True, allow_reentry=True, conversation_timeout=20
)
dp.add_handler(tell_handler)

settings_gui_handler = ConversationHandler(
    entry_points=[CommandHandler('settings', settings_gui.start)],

    states={
        settings_gui.UPDATED: [CallbackQueryHandler(settings_gui.change_prob, pattern="MEDIA_PROB|PROFANE_PROB"),
                               CallbackQueryHandler(settings_gui.morn_swap, pattern="Morning"),
                               CallbackQueryHandler(settings_gui.save, pattern="SAVE")
                               ],

        settings_gui.PROBABILITY:
            [CallbackQueryHandler(settings_gui.prob_updater, pattern="0.0|-0.1|-0.05|0.05|0.1|1.0"),
             CallbackQueryHandler(settings_gui.go_back, pattern="Back")
             ]
    },
    fallbacks=[CommandHandler('cancel', settings_gui.save)]
)
dp.add_handler(settings_gui_handler)

media_filters = (Filters.document | Filters.photo | Filters.video | Filters.voice)
edit_filter = Filters.update.edited_message

dp.add_handler(MessageHandler(media_filters, media))
dp.add_handler(MessageHandler(Filters.status_update.pinned_message & Filters.user(username=testbot), del_pin))
dp.add_handler(MessageHandler(Filters.reply & Filters.group & ~ edit_filter, reply))
dp.add_handler(MessageHandler(Filters.regex(testbot) & Filters.group & ~ edit_filter & ~ Filters.command, private))
dp.add_handler(MessageHandler(Filters.group & Filters.text & ~ edit_filter, group))
dp.add_handler(MessageHandler(Filters.private & Filters.text & ~ edit_filter, private))
dp.add_handler(MessageHandler(Filters.command, bc.unknown))

updater.job_queue.run_repeating(bday_wish, 86400, first=1)  # Will run every time script is started, and once a day.
updater.job_queue.run_repeating(morning_goodness, 86400, first=1)
prettyprintview()

updater.start_polling()
updater.idle()
