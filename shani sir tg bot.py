import logging
import random
from datetime import time
from difflib import get_close_matches
from time import sleep
from uuid import uuid4

from telegram import InlineQueryResultCachedAudio
from telegram.ext import CommandHandler
from telegram.ext import InlineQueryHandler
from telegram.ext import MessageHandler, Filters
from telegram.ext import Updater

logging.basicConfig(format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
                    level=logging.INFO)
updater = Updater(token='', use_context=True)
dispatcher = updater.dispatcher

results = []
begin = 0

with open("file_ids.txt", "r") as ids, open("names.txt", "r") as name:
    file_ids = ids.read().strip().split(',')
    names = name.read().strip().split(',')

assert (len(names) == len(file_ids))
for file_id, name in zip(file_ids, names):
    results.append(InlineQueryResultCachedAudio(
        id=uuid4(),
        audio_file_id=file_id,
        caption=name))


def start(update, context):
    context.bot.send_message(chat_id=update.effective_chat.id,
                             text="You can use me anywhere, @ me in the chatbox and type to get an audio clip. Or just"
                                  " talk to me here and get help from me directly.")


def helper(update, context):
    context.bot.send_message(chat_id=update.effective_chat.id,
                             text="This bot sends you actual shani sir clips straight from Shanisirmodule! He is savage"
                                  " in groups too! More commands will be added in the future."
                                  " P.S: Download Shanisirmodule from:"
                                  " https://github.com/tmslads/Shanisirmodule/releases")


def secret(update, context):
    context.bot.send_message(chat_id=update.effective_chat.id, text="stop finding secret commands :P")


def unknown(update, context):
    context.bot.send_message(chat_id=update.effective_chat.id, text="Sorry, I didn't understand that command.")


def private(update, context):
    global begin

    # cleaned = []
    # JJ_RB = ["like you say", "like you speak", "not hard", "okay, fine?"]  # For Adjectives or Adverbs
    #
    # msg = update.message.text
    #
    # punctuation = r"""!"#$%&'()*+,-./:;<=>?@[\]^_`{|}~"""
    # msg = ''.join(c for c in msg if c not in punctuation)
    # blob = TextBlob(msg)
    # cleaned = blob.words  # Returns list with no punctuation marks
    # blob_tags_iter = iter(blob.tags)
    #
    # flag = 0  # To check if a modal is present in the sentence
    # lydcount = 0  # Counts the number of times "like you do" has been added
    # JJ_RBcount = 0  # Counts the number of times a phrase from JJ_RB has been added
    # if len(cleaned) < 15:
    #     lydlim = 2  # to limit the number of times we add
    #     JJ_RBlim = 2  # lyd and JJ_RB
    # else:
    #     lydlim = len(cleaned) // 9
    #     JJ_RBlim = len(cleaned) // 9
    # for word, tag in blob_tags_iter:  # returns list of tuples which tells the POS
    #     index = cleaned.index(word)
    #
    #     if tag == 'MD' and not flag:  # Modal
    #         cleaned.insert(index + 1, "(if the laws of physics allow it)")
    #         flag = 1
    #
    #     if tag in ['JJ', 'JJR', 'JJS', 'RB', 'RBR', 'RBS'] and JJ_RBcount < JJ_RBlim:  # Adjective or Adverb
    #         cleaned.insert(index + 1, random.choice(JJ_RB))
    #         JJ_RBcount += 1
    #
    #     elif tag in ['VB', 'VBD', 'VBG', 'VBN', 'VBP', 'VBZ'] and lydcount < lydlim:  # Verb
    #         cleaned.insert(index + 1, "like you do")
    #         lydcount += 1
    #
    # if random.choice([0, 1]):
    #     cleaned.append(random.choice(["I am so sowry", "i don't want to talk like that", "*scratches nose*",
    #                                   "it is embarrassing to me like basically", "it's not to trouble you like you say",
    #                                   "go for the worksheet"]))
    # else:
    #     cleaned.append(random.choice(["this will be fruitful", "you will benefit", "that is the expected behaviour",
    #                                   "now you are on the track like", "class is in the flow like",
    #                                   "aim to hit the tarjit",
    #                                   "don't press the jockey"]))
    with open("interactions.txt", "a") as f:
        msg = f"\n\nUTC+0 {update.message.date} {update.message.from_user.first_name} says: {update.message.text}"
        if update.message.reply_to_message:  # If user is replying to bot directly
            out = 'ok'
        else:
            out = f"Good morning {update.message.from_user.first_name} " \
              f"so sowry I am sick today I can't speak to you today like you say"
        print(msg)
        print(out)
        f.write(msg)
        f.write(f"\nOutput: {out}")

    context.bot.send_chat_action(chat_id=update.effective_chat.id, action='typing')
    sleep((25 / 60) * len(out.split())) if (25 / 60) * len(out.split()) < 6 else sleep(6)  # Assuming 25 WPM typing speed on a phone
    update.effective_message.reply_text(out)

    # print(time())
    # print(time.time() - begin)
    begin = update.message.date
    # cleaned.insert(0, 'good mourning')
    #
    # if len(cleaned) < 5:  # Will run if input is too short
    #     cleaned.append("*draws perfect circle*")
    #
    # if 'when' in cleaned or 'When' in cleaned:  # If question is present in input then-
    #     cleaned.append('decide a date')
    #
    # shanitext = ' '.join(cleaned).capitalize()

    # print(shanitext)
    # context.bot.send_message(chat_id=update.effective_chat.id, text=shanitext)


def morning_goodness(context):
    context.bot.send_message(chat_id=-1001396726510, text="Good morning everyone")
    context.bot.send_chat_action(chat_id=-1001396726510, action='upload_audio')
    sleep(1)
    context.bot.send_audio(chat_id=-1001396726510, audio=open(r'Assets/clips/good mourning.mp3', 'rb'),
                           title="Good morning")
    context.bot.send_chat_action(chat_id=-1001396726510, action='typing')
    sleep((25 / 60) * 10)
    context.bot.send_message(chat_id=-1001396726510, text="I am sick today, thank you for your well wishes.")


def inline_clips(update, context):
    query = update.inline_query.query
    if not query:
        random.shuffle(results)
        context.bot.answer_inline_query(update.inline_query.id, results[:25])
    else:
        matches = get_close_matches(query, names, n=15, cutoff=0.4)
        index = 0
        while index <= len(matches) - 1:
            for pos, result in enumerate(results):
                if index == len(matches):
                    break
                if matches[index] == result['caption']:
                    results[index], results[pos] = results[pos], results[index]
                    index += 1

        context.bot.answer_inline_query(update.inline_query.id, results[:16])


inline_clips_handler = InlineQueryHandler(inline_clips)
dispatcher.add_handler(inline_clips_handler)

help_handler = CommandHandler('help', helper)
dispatcher.add_handler(help_handler)

clip_handler = CommandHandler('secret', secret)
dispatcher.add_handler(clip_handler)

start_handler = CommandHandler('start', start)
dispatcher.add_handler(start_handler)

private_handler = MessageHandler(Filters.text, private)
dispatcher.add_handler(private_handler)

unknown_handler = MessageHandler(Filters.command, unknown)
dispatcher.add_handler(unknown_handler)

updater.job_queue.run_daily(morning_goodness, time(8, 00, 00))  # sends message everyday at 8am on the group
updater.start_polling()
updater.idle()
