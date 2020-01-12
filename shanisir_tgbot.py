import getpass
import itertools
import logging
import random as r
from datetime import time
from difflib import get_close_matches
from time import sleep
from uuid import uuid4

import chatterbot
import emoji
from telegram import InlineQueryResultAudio
from telegram.ext import CommandHandler
from telegram.ext import InlineQueryHandler
from telegram.ext import MessageHandler, Filters
from telegram.ext import Updater
from textblob import TextBlob

import chatbot
import commands
import util
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
dispatcher = updater.dispatcher

latest_response = None
frequency = 0

results = []
rebukes = ["this is not the expected behaviour", "i don't want you to talk like that",
           "this language is embarassing to me like basically", "this is not a fruitful conversation"]

r.shuffle(rebukes)
rebukes = itertools.cycle(rebukes)
links, names = util.clips()

for clip in zip(links, names):
    results.append(InlineQueryResultAudio(id=uuid4(),
                                          audio_url=clip[0], title=clip[1], performer="Shani Sir"))


def inline_clips(update, context):
    query = update.inline_query.query
    if not query:
        context.bot.answer_inline_query(update.inline_query.id, results[:50])
    else:
        matches = get_close_matches(query, names, n=15, cutoff=0.3)
        index = 0
        while index <= len(matches) - 1:
            for pos, result in enumerate(results):
                if index == len(matches):
                    break
                if matches[index] == result['title']:
                    results[index], results[pos] = results[pos], results[index]
                    index += 1

        context.bot.answer_inline_query(inline_query_id=update.inline_query.id, results=results[:16])


def media(update, context):
    try:
        doc = update.message.document.file_name[-3:]
    except Exception:
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

    doc_reactions = ["Is this a virus", "I suggest like you say you don't open this", "We just don't mind that okay?"]

    context.bot.send_chat_action(chat_id=update.effective_chat.id, action='typing')
    sleep(2)
    if update.message.photo and r.choices([0, 1], weights=[0.6, 0.4])[0]:
        print("Img")
        context.bot.send_message(chat_id=update.effective_chat.id, text=r.choice(img_reactions),
                                 reply_to_message_id=msg)

    elif update.message.voice and r.choices([0, 1], weights=[0.6, 0.4])[0]:
        print("voiceee")
        context.bot.send_message(chat_id=update.effective_chat.id, text=r.choice(voice_reactions),
                                 reply_to_message_id=msg)

    elif (update.message.video or doc == 'mp4' or doc == 'gif') and r.choices([0, 1], weights=[0.6, 0.4])[0]:
        print("vid")
        context.bot.send_message(chat_id=update.effective_chat.id, text=r.choice(vid_reactions),
                                 reply_to_message_id=msg)

    elif (doc == 'apk' or doc == 'exe') and r.choices([0, 1], weights=[0.6, 0.4])[0]:
        context.bot.send_message(chat_id=update.effective_chat.id, text=r.choice(doc_reactions),
                                 reply_to_message_id=msg)
        print("app")


def reply(update, context):
    if update.message.reply_to_message.from_user.username == 'shanisirbot':  # If reply is from bot:
        private(update, context, grp=True,
                the_id=update.message.message_id)  # send a response as you would in private chat


def group(update, context):
    if any(bad_word in update.message.text.lower().split() for bad_word in prohibited):
        if r.choices([0, 1], weights=[0.8, 0.2])[0]:  # Probabilities are 0.8 - False, 0.2 - True.
            out = f"{next(rebukes)} {update.message.from_user.first_name}"
            context.bot.send_message(chat_id=update.effective_chat.id, text=out,
                                     reply_to_message_id=update.message.message_id)  # Sends message
            print(f"Rebuke: {out}")


def private(update, context, grp=False, the_id=None, isgrp="(PRIVATE)"):
    global frequency, latest_response
    cleaned = []
    JJ_RB = ["like you say", "like you speak"]  # For Adjectives or Adverbs
    initialStatement = chatterbot.conversation.Statement(update.message.text, in_response_to=latest_response)

    if grp:
        isgrp = f"(GROUP: {update.effective_chat.title})"
        initial = update.message.reply_to_message.text
    else:
        initial = update.message.text
        chatbot.shanisirbot.learn_response(initialStatement,
                                           latest_response)  # Learn user's latest message as response to bot's message

    latest_response = chatbot.shanisirbot.get_response(initial)
    try:
        msg = latest_response.text
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
        inp = f"UTC+0 {update.message.date} {isgrp} {update.message.from_user.full_name}" \
              f" ({update.message.from_user.username}) says: {update.message.text}\n"
        out = shanitext.capitalize()
        print(f"{inp}\n{out}")
        f1.write(emoji.demojize(inp))
        f1.write(f"Output: {emoji.demojize(out)}\n\n")
        context.bot.send_chat_action(chat_id=update.effective_chat.id, action='typing')  # Sends 'typing...' status
        # Assuming 25 WPM typing speed on a phone
        time_taken = (25 / 60) * len(out.split())
        sleep(time_taken) if time_taken < 6 else sleep(6)
        context.bot.send_message(chat_id=update.effective_chat.id, text=out,
                                 reply_to_message_id=the_id)  # Sends message


def morning_goodness(context):
    with open("text_files/seek.txt", "r+") as seek, open("text_files/good_mourning.txt", "r") as greetings:
        cursor = int(seek.read())  # Finds where the cursor stopped on the previous day

        if cursor == 16157:  # If EOF was reached
            cursor = 0  # Start from the beginning

        greetings.seek(cursor)  # Move the cursor to its previous position
        greeting = greetings.readline()  # And read the next line
        print(greeting)
        cursor = greetings.tell()  # Position of cursor after reading the greeting
        seek.seek(0)
        seek.write(str(cursor))  # Store the new position of the cursor, for next morning_goodness() call
        seek.truncate()

    for chat_id in [-1001396726510, -1001210862980]:
        msg = context.bot.send_message(chat_id=chat_id, text=greeting)  # Send to both groups
        context.bot.pin_chat_message(chat_id=chat_id, message_id=msg.message_id)  # Pin it
        context.bot.send_chat_action(chat_id=chat_id, action='upload_audio')
        context.bot.send_audio(chat_id=chat_id, audio=open(f"{clip_loc}my issue is you don't score.mp3", 'rb'),
                               title="Good morning")


inline_clips_handler = InlineQueryHandler(inline_clips)
dispatcher.add_handler(inline_clips_handler)

help_handler = CommandHandler('help', commands.BotCommands.helper)
dispatcher.add_handler(help_handler)

clip_handler = CommandHandler('secret', commands.BotCommands.secret)
dispatcher.add_handler(clip_handler)

start_handler = CommandHandler('start', commands.BotCommands.start)
dispatcher.add_handler(start_handler)

swear_handler = CommandHandler('swear', commands.BotCommands.swear)
dispatcher.add_handler(swear_handler)

snake_handler = CommandHandler('snake', commands.BotCommands.snake)
dispatcher.add_handler(snake_handler)

facts_handler = CommandHandler('facts', commands.BotCommands.facts)
dispatcher.add_handler(facts_handler)

media_handler = MessageHandler(Filters.document | Filters.photo | Filters.video | Filters.voice, media)
dispatcher.add_handler(media_handler)

reply_handler = MessageHandler(Filters.reply & Filters.group, reply)
dispatcher.add_handler(reply_handler)

group_handler = MessageHandler(Filters.group, group)
dispatcher.add_handler(group_handler)

private_handler = MessageHandler(Filters.text, private)
dispatcher.add_handler(private_handler)

unknown_handler = MessageHandler(Filters.command, commands.BotCommands.unknown)
dispatcher.add_handler(unknown_handler)

updater.job_queue.run_daily(morning_goodness, time(8, 0, 0))  # morning_goodness() will be called daily at that time
updater.start_polling()
updater.idle()
