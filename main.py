import getpass
import itertools
import logging
import random as r
from datetime import time
from time import sleep

import chatterbot
import emoji
from telegram.ext import CommandHandler
from telegram.ext import ConversationHandler
from telegram.ext import InlineQueryHandler
from telegram.ext import MessageHandler, Filters
from telegram.ext import Updater
from textblob import TextBlob

import chatbot
import commands
import conversation
import inline
from commands import prohibited

logging.basicConfig(format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
                    level=logging.INFO)

chatbot.shanisirbot.initialize()  # Does any work that needs to be done before the chatbot can process responses.

user = getpass.getuser()  # To determine which location to provide for clips
if user == 'Uncle Sam':
    clip_loc = r'C:/Users/Uncle Sam/Desktop/sthyaVERAT/4 FUN ya Practice/Shanisirmodule/Assets/clips/'
elif user == 'aarti':
    clip_loc = r'C:/Users/aarti/Documents/Python stuff/Bored/Shanisirmodule/Assets/clips/'

with open("text_files/token.txt", 'r') as file:
    bot_token = file.read()

updater = Updater(token=f'{bot_token}', use_context=True)
                  # request_kwargs={'proxy_url': 'socks5://grsst.s5.opennetwork.cc:999',  # Connect with socks5 proxy
                                  # 'urllib3_proxy_kwargs': {'username': '476269395', 'password': 'eWiS7xd8'}})
dispatcher = updater.dispatcher
tg_bot = updater.bot

bot_response = None

rebukes = ["this is not the expected behaviour", "i don't want you to talk like that",
           "this language is embarassing to me like basically", "this is not a fruitful conversation"]

r.shuffle(rebukes)
rebukes = itertools.cycle(rebukes)


def media(update, context):
    """Sends a reaction to media messages (pictures, videos, documents, voice notes)"""

    try:
        doc = update.message.document.file_name[-3:]
    except AttributeError:  # When there is no document sent
        doc = ''
    name = update.message.from_user.first_name
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
        tg_bot.send_chat_action(chat_id=update.effective_chat.id, action='typing')
        sleep(2)

        if update.message.photo:
            print("Img")
            tg_bot.send_message(chat_id=update.effective_chat.id, text=r.choice(img_reactions),
                                reply_to_message_id=msg)

        elif update.message.voice:
            print("voiceee")
            tg_bot.send_message(chat_id=update.effective_chat.id, text=r.choice(voice_reactions),
                                reply_to_message_id=msg)

        elif update.message.video or doc == 'mp4' or doc == 'gif':
            print("vid")
            tg_bot.send_message(chat_id=update.effective_chat.id, text=r.choice(vid_reactions),
                                reply_to_message_id=msg)

        elif doc == 'apk' or doc == 'exe':
            tg_bot.send_message(chat_id=update.effective_chat.id, text=r.choice(app_reactions),
                                reply_to_message_id=msg)
            print("app")


def del_pin(update, context):
    """Deletes pinned message service status from the bot."""

    if update.message.from_user.username == 'shanisirbot':
        tg_bot.delete_message(chat_id=update.effective_chat.id, message_id=update.message.message_id)


def reply(update, context):
    if update.message.reply_to_message.from_user.username == 'shanisirbot':  # If reply is from bot:
        private(update, context, grp=True,
                the_id=update.message.message_id)  # send a response as you would in private chat


def group(update, context):
    """Checks for profanity in messages and responds to that."""

    if update.message is not None and update.message.text is not None:
        if any(bad_word in update.message.text.lower().split() for bad_word in prohibited):
            if r.choices([0, 1], weights=[0.8, 0.2])[0]:  # Probabilities are 0.8 - False, 0.2 - True.
                out = f"{next(rebukes)} {update.message.from_user.first_name}"
                tg_bot.send_message(chat_id=update.effective_chat.id, text=out,
                                    reply_to_message_id=update.message.message_id)  # Sends message
                print(f"Rebuke: {out}")


def private(update, context, grp=False, the_id=None, isgrp="(PRIVATE)"):
    global bot_response
    cleaned = []
    JJ_RB = ["like you say", "like you speak"]  # For Adjectives or Adverbs

    if update.message.reply_to_message is not None:  # If the user's message is a reply to a previous message from the bot
        bot_response = update.message.reply_to_message.text
    user_msg = chatterbot.conversation.Statement(update.message.text, in_response_to=bot_response)
    reply = f"(REPLY TO [{user_msg.in_response_to}])"

    if grp:
        isgrp = f"(GROUP: {update.effective_chat.title})"
    else:
        chatbot.shanisirbot.learn_response(user_msg,
                                           bot_response)  # Learn user's latest message (user_msg) as response to bot's last message (bot_response)

    bot_response = chatbot.shanisirbot.get_response(user_msg.text)
    try:
        msg = bot_response.text
    except AttributeError:
        msg = 'Hello'

    punctuation = r"""!"#$%&'()*+,-./:;<=>?@[\]^_`{|}~"""
    msg = ''.join(c for c in msg if c not in punctuation)
    blob = TextBlob(msg)
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

    if r.choice([0, 1]):
        if r.choice([0, 1]):
            cleaned.append(r.choice(["I am so sowry", "i don't want to talk like that",
                                     "it is embarrassing to me like basically", "it's not to trouble you like you say",
                                     "go for the worksheet", "it's not that hard"]))
        else:
            cleaned.append(r.choice(["it will be fruitful", "you will benefit", "that is the expected behaviour",
                                     "now you are on the track like", "now class is in the flow like",
                                     "aim to hit the tarjit", "don't press the jockey"]))
        cleaned.insert(0, update.message.from_user.first_name)
    else:
        cleaned.append(update.message.from_user.first_name)

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
        tg_bot.send_chat_action(chat_id=update.effective_chat.id, action='typing')  # Sends 'typing...' status for 6 sec
        # Assuming 25 WPM typing speed on a phone
        time_taken = (25 / 60) * len(out.split())
        sleep(time_taken) if time_taken < 6 else sleep(6)  # Sends status for 6 seconds if message is too long to type
        tg_bot.send_message(chat_id=update.effective_chat.id, text=out,
                            reply_to_message_id=the_id)  # Sends message


def morning_goodness():
    """Send a "good morning" quote to the groups, along with a clip"""

    with open("text_files/seek.txt", "r+") as seek, open("text_files/good_mourning.txt", "r") as greetings:
        cursor = int(seek.read())  # Finds where the cursor stopped on the previous day

        if cursor == 13642:  # If EOF was reached
            cursor = 0  # Start from the beginning

        greetings.seek(cursor)  # Move the cursor to its previous position
        greeting = greetings.readline()  # And read the next line
        print(greeting)
        cursor = greetings.tell()  # Position of cursor after reading the greeting
    seek = open("text_files/seek.txt", "w")
    seek.write(str(cursor))  # Store the new position of the cursor, to be used when morning_goodness() is next called
    seek.close()

    for chat_id in [-1001396726510, -1001210862980]:
        msg = tg_bot.send_message(chat_id=chat_id, text=greeting)  # Send to both groups
        tg_bot.pin_chat_message(chat_id=chat_id, message_id=msg.message_id, disable_notification=True)  # Pin it
        tg_bot.send_chat_action(chat_id=chat_id, action='upload_audio')
        tg_bot.send_audio(chat_id=chat_id, audio=open(f"{clip_loc}my issue is you don't score.mp3", 'rb'),
                          title="Good morning")


inline_clips_handler = InlineQueryHandler(inline.inline_clips)
dispatcher.add_handler(inline_clips_handler)

help_handler = CommandHandler(command='help', callback=commands.BotCommands.helper)
dispatcher.add_handler(help_handler)

clip_handler = CommandHandler(command='secret', callback=commands.BotCommands.secret)
dispatcher.add_handler(clip_handler)

start_handler = CommandHandler(command='start', callback=commands.BotCommands.start)
dispatcher.add_handler(start_handler)

swear_handler = CommandHandler(command='swear', callback=commands.BotCommands.swear)
dispatcher.add_handler(swear_handler)

snake_handler = CommandHandler(command='snake', callback=commands.BotCommands.snake)
dispatcher.add_handler(snake_handler)

facts_handler = CommandHandler(command='facts', callback=commands.BotCommands.facts)
dispatcher.add_handler(facts_handler)

# Can start the conversation two ways:
# 1. By directly entering command or
# 2. Replying to a message (which is hopefully a yes/no question) and then typing an additional message (optional),
#    NOTE: Message must start with /8ball if it is placed anywhere else, it won't work.
# Refer https://python-telegram-bot.readthedocs.io/en/stable/telegram.ext.conversationhandler.html for syntax, etc.
convo_handler = ConversationHandler(
    entry_points=[CommandHandler(command="8ball", callback=conversation.thinking, filters=Filters.reply),
                  CommandHandler(command="8ball", callback=conversation.magic8ball)],


    states={conversation.PROCESSING: [MessageHandler(filters=Filters.reply & Filters.text,
                                                     callback=conversation.thinking)]},

    fallbacks=[CommandHandler(command='cancel', callback=conversation.cancel)]
)
dispatcher.add_handler(convo_handler)

media_handler = MessageHandler(Filters.document | Filters.photo | Filters.video | Filters.voice, media)
dispatcher.add_handler(media_handler)

del_pinmsg_handler = MessageHandler(Filters.status_update.pinned_message, del_pin)
dispatcher.add_handler(del_pinmsg_handler)

reply_handler = MessageHandler(Filters.reply & Filters.group, reply)
dispatcher.add_handler(reply_handler)

group_handler = MessageHandler(Filters.group, group)
dispatcher.add_handler(group_handler)

private_handler = MessageHandler(Filters.private, private)
dispatcher.add_handler(private_handler)

unknown_handler = MessageHandler(Filters.command, commands.BotCommands.unknown)
dispatcher.add_handler(unknown_handler)

# Note: time values passed are in UTC+0
updater.job_queue.run_daily(morning_goodness, time(4, 0, 0))  # will be called daily at ([h]h, [m]m,[s]s)
updater.start_polling()
