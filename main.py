import itertools
import logging
import random as r
from datetime import time
from time import sleep

import chatterbot
import emoji
from telegram.ext import (CommandHandler, ConversationHandler, InlineQueryHandler, MessageHandler, Filters,
                          PicklePersistence, Updater)
from textblob import TextBlob

import chatbot
import gcalendar
import inline
from commands import BotCommands as bc, prohibited
from constants import group_ids
from convos import (bday_convo as bday, magic_convo as magic, nick_convo as nick)
from convos import start

logging.basicConfig(format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
                    level=logging.INFO)

chatbot.shanisirbot.initialize()  # Does any work that needs to be done before the chatbot can process responses.
get_tags = chatbot.shanisirbot.storage.tagger.get_bigram_pair_string

with open("text_files/token.txt", 'r') as file:
    bot_token = file.read()

pp = PicklePersistence(filename=r'text_files/user_data')
updater = Updater(token=f'{bot_token}', use_context=True, persistence=pp)

dispatcher = updater.dispatcher
shanisir_bot = updater.bot

bot_response = None

rebukes = ["this is not the expected behaviour", "i don't want you to talk like that",
           "this language is embarrassingassing to me like basically", "this is not a fruitful conversation"]

r.shuffle(rebukes)
rebukes = itertools.cycle(rebukes)


def nicknamer(update, context):
    """Uses current nickname set by user."""

    try:
        name = context.user_data['nickname'][-1]
    except (KeyError, IndexError):
        context.user_data['nickname'] = []
        context.user_data['nickname'].append(update.message.from_user.first_name)
    finally:
        return context.user_data['nickname'][-1]


def media(update, context):
    """Sends a reaction to media messages (pictures, videos, documents, voice notes)"""

    try:
        doc = update.message.document.file_name[-3:]
    except AttributeError:  # When there is no document sent
        doc = ''
    name = nicknamer(update, context)

    msg = update.message.message_id

    img_reactions = ["😂", "🤣", "😐", f"Not funny {name} okay?", "This is not fine like you say", "*giggles*",
                     f"this is embarrassing to me {name}", "What your doing?! Go for the worksheet"]

    vid_reactions = ["😂", "🤣", "😐", f"I've never seen anything like this {name}", "What is this",
                     "Now I feel very bad like", f"Are you fine {name}?"]

    voice_reactions = ["What is this", f"I can't hear you {name}", f"Are you fine {name}?",
                       "Now your on the track like", "Your voice is like you say bad",
                       f"See I can't tolerate this {name}"]

    app_reactions = ["Is this a virus", "I suggest like you say you don't open this", "We just don't mind that okay?"]

    prob = r.choices([0, 1], weights=[0.6, 0.4])[0]
    if prob:
        shanisir_bot.send_chat_action(chat_id=update.effective_chat.id, action='typing')
        sleep(2)

        if update.message.photo:
            print("Img")
            shanisir_bot.send_message(chat_id=update.effective_chat.id, text=r.choice(img_reactions),
                                      reply_to_message_id=msg)

        elif update.message.voice:
            print("voiceee")
            shanisir_bot.send_message(chat_id=update.effective_chat.id, text=r.choice(voice_reactions),
                                      reply_to_message_id=msg)

        elif update.message.video or doc == 'mp4' or doc == 'gif':
            print("vid")
            shanisir_bot.send_message(chat_id=update.effective_chat.id, text=r.choice(vid_reactions),
                                      reply_to_message_id=msg)

        elif doc == 'apk' or doc == 'exe':
            shanisir_bot.send_message(chat_id=update.effective_chat.id, text=r.choice(app_reactions),
                                      reply_to_message_id=msg)
            print("app")


def del_pin(update, context):
    """Deletes pinned message service status from the bot."""

    if update.message.from_user.username == 'shanisirbot':
        shanisir_bot.delete_message(chat_id=update.effective_chat.id, message_id=update.message.message_id)


def reply(update, context):
    if update.message.reply_to_message.from_user.username == 'shanisirbot':  # If reply is from bot:
        private(update, context, grp=True,
                the_id=update.message.message_id)  # send a response as you would in private chat


def group(update, context):
    """Checks for profanity in messages and responds to that."""

    if any(bad_word in update.message.text.lower().split() for bad_word in prohibited):
        if r.choices([0, 1], weights=[0.8, 0.2])[0]:  # Probabilities are 0.8 - False, 0.2 - True.
            name = nicknamer(update, context)

            out = f"{next(rebukes)} {name}"
            shanisir_bot.send_message(chat_id=update.effective_chat.id, text=out,
                                      reply_to_message_id=update.message.message_id)  # Sends message
            print(f"Rebuke: {out}")


def private(update, context, grp=False, the_id=None, isgrp="(PRIVATE)"):
    global bot_response

    user = update.message.from_user
    chat_id = update.effective_chat.id

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
        context.chat_data["chat_ids"] = []

    elif chat_id not in context.chat_data['chat_ids']:  # Gets chat id of the user in which they have talked to the bot
        context.chat_data['chat_ids'].append(chat_id)

    cleaned = []
    JJ_RB = ["like you say", "like you speak"]  # For Adjectives or Adverbs

    msg_text = update.message.text

    if bot_response is None:
        temp = None
        search_in_response_text = None
    else:
        temp = bot_response.text
        search_in_response_text = get_tags(temp)

    # If the user's message is a reply to a message
    if update.message.reply_to_message is not None:
        reply_text = update.message.reply_to_message.text

        bot_response = chatterbot.conversation.Statement(text=reply_text,
                                                         search_text=get_tags(reply_text))
        user_msg = chatterbot.conversation.Statement(text=msg_text,
                                                     search_text=get_tags(msg_text),
                                                     in_response_to=bot_response,
                                                     search_in_response_to=get_tags(
                                                         reply_text))
    else:
        user_msg = chatterbot.conversation.Statement(text=msg_text,
                                                     search_text=get_tags(msg_text),
                                                     in_response_to=bot_response,
                                                     search_in_response_to=search_in_response_text)

    reply = f"(REPLY TO [{user_msg.in_response_to}])"

    if grp:
        isgrp = f"(GROUP: {update.effective_chat.title})"
    else:  # Learn user's latest message (user_msg) as response to bot's last message (bot_response)
        chatbot.shanisirbot.learn_response(user_msg,
                                           bot_response)

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

    if 'when' in cleaned or 'When' in cleaned or 'time' in cleaned or 'Time' in cleaned:  # If question is present
        cleaned.insert(-1, 'decide a date')

    for word in update.message.text:
        if word in emoji.UNICODE_EMOJI:  # Checks if emoji is present in message
            cleaned.append(r.choice(list(emoji.UNICODE_EMOJI)))  # Adds a random emoji

    shanitext = ' '.join(cleaned).capitalize()

    with open("text_files/interactions.txt", "a") as f1:
        inp = f"UTC+0 {update.message.date} {isgrp} {reply} {update.message.from_user.full_name}" \
              f" ({update.message.from_user.username}) SAID: {update.message.text}\n"
        out = shanitext.capitalize()
        print(f"{inp}\n{out}")
        f1.write(emoji.demojize(inp))
        f1.write(f"BOT REPLY: {emoji.demojize(out)}\n\n")
        shanisir_bot.send_chat_action(chat_id=update.effective_chat.id,
                                      action='typing')  # Sends 'typing...' status for 6 sec
        # Assuming 25 WPM typing speed on a phone
        time_taken = (25 / 60) * len(out.split())
        sleep(time_taken) if time_taken < 6 else sleep(6)  # Sends status for 6 seconds if message is too long to type
        shanisir_bot.send_message(chat_id=update.effective_chat.id, text=out,
                                  reply_to_message_id=the_id)  # Sends message


def morning_goodness(context):
    """Send a "good morning" quote to the groups, along with a clip"""

    with open("text_files/good_mourning.txt", "r") as greetings:
        position = context.bot_data['seek']
        if position == 13642:  # If EOF was reached
            position = 0  # Start from the beginning
        greetings.seek(position)

        greeting = greetings.readline()
        print(greeting)
        context.bot_data['seek'] = greetings.tell()

    for chat_id in (group_ids['12b'], group_ids['grade12']):  # Send to groups: [12B, Grade 12]
        msg = shanisir_bot.send_message(chat_id=chat_id, text=greeting)  # Send to both groups
        shanisir_bot.pin_chat_message(chat_id=chat_id, message_id=msg.message_id, disable_notification=True)  # Pin it
        shanisir_bot.send_chat_action(chat_id=chat_id, action='upload_audio')
        shanisir_bot.send_audio(chat_id=chat_id,
                                audio="https://raw.githubusercontent.com/tmslads/Shanisirmodule/haunya/Assets/"
                                      "clips/my%20issue%20is%20you%20don't%20score.mp3",
                                title="Good morning")


def bday_wish(context):
    """Wishes you on your birthday."""
    gcalendar.main()
    days_remaining, name = gcalendar.get_next_bday()

    # Wishes from Google Calendar-
    if days_remaining == 0:
        context.bot.send_message(chat_id=group_ids['12b'],
                                 text=f"Happy birthday {name}! May the mass times acceleration be with you!🎉")

    # Wishes from /tell birthday input-
    # WIP


dispatcher.add_handler(InlineQueryHandler(inline.inline_clips))
dispatcher.add_handler(CommandHandler(command='help', callback=bc.helper))
dispatcher.add_handler(CommandHandler(command='secret', callback=bc.secret))
dispatcher.add_handler(CommandHandler(command='start', callback=bc.start))
dispatcher.add_handler(CommandHandler(command='swear', callback=bc.swear))
dispatcher.add_handler(CommandHandler(command='snake', callback=bc.snake))
dispatcher.add_handler(CommandHandler(command='facts', callback=bc.facts))

# /8ball conversation-
convo_handler = ConversationHandler(
    entry_points=[
        CommandHandler(command="8ball", callback=magic.magic8ball),
        MessageHandler(filters=Filters.command(False) & Filters.text & Filters.regex("8ball"),
                       callback=magic.thinking)],

    states={magic.PROCESSING: [
        MessageHandler(filters=(Filters.reply & Filters.text), callback=magic.thinking)]},

    fallbacks=[CommandHandler(command='cancel', callback=magic.cancel)], conversation_timeout=15
)
dispatcher.add_handler(convo_handler)

# /tell conversation
convo2_handler = ConversationHandler(
    entry_points=[CommandHandler('tell', start.initiate)],
    states={
        start.CHOICE: [MessageHandler(filters=Filters.regex("^Birthday$"), callback=bday.bday),
                       MessageHandler(filters=Filters.regex("^Nickname$"), callback=nick.nick),
                       MessageHandler(filters=Filters.regex("^Nothing$"), callback=start.leave)
                       ],
        bday.INPUT: [
            MessageHandler(
                filters=Filters.regex("^([1-9][0-9]{3}-[0-9]{2}-[0-9]{2})$"),
                # Regex to see if you've added a valid date
                callback=bday.bday_add_or_update),
            MessageHandler(filters=Filters.text, callback=bday.wrong)],  # Accepts only dates

        bday.MODIFY: [MessageHandler(filters=Filters.regex("^Forget my birthday sir$"), callback=bday.bday_del),

                      MessageHandler(filters=Filters.regex("^Update my birthday sir$"),
                                     callback=bday.bday_mod)
                      ],
        nick.SET_NICK: [MessageHandler(filters=Filters.text & Filters.reply, callback=nick.add_edit_nick)],

        nick.MODIFY_NICK: [MessageHandler(filters=Filters.regex("^Change nickname$"), callback=nick.edit_nick),
                           MessageHandler(filters=Filters.regex("^Remove nickname$"), callback=nick.del_nick),
                           MessageHandler(filters=Filters.regex("^Back$"), callback=nick.back)
                           ],
    },
    fallbacks=[MessageHandler(Filters.regex("^No, thank you sir$"), callback=bday.reject),
               CommandHandler("cancel", start.leave)],

    name="/tell convo",
    persistent=True, allow_reentry=True, conversation_timeout=15
)
dispatcher.add_handler(convo2_handler)

media_handler = MessageHandler(Filters.document | Filters.photo | Filters.video | Filters.voice, media)
dispatcher.add_handler(media_handler)

del_pinmsg_handler = MessageHandler(Filters.status_update.pinned_message, del_pin)
dispatcher.add_handler(del_pinmsg_handler)

reply_handler = MessageHandler(Filters.reply & Filters.group, reply)
dispatcher.add_handler(reply_handler)

group_handler = MessageHandler(Filters.group & Filters.text, group)
dispatcher.add_handler(group_handler)

private_handler = MessageHandler(Filters.private, private)
dispatcher.add_handler(private_handler)

unknown_handler = MessageHandler(Filters.command, bc.unknown)
dispatcher.add_handler(unknown_handler)

# Note: time values passed are in UTC+0
updater.job_queue.run_daily(morning_goodness, time(4, 0, 0))  # will be called daily at ([h]h, [m]m,[s]s)
updater.job_queue.run_repeating(bday_wish, 86400, first=1)  # Will run every time script is started, and once a day.
updater.start_polling()
