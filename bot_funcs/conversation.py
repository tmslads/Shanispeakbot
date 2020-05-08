import random as r
import re

import chatterbot
import emoji
from telegram import Update
from telegram.ext import CallbackContext
from textblob import TextBlob

from chatbot import get_tags, shanisirbot
from bot_funcs.commands import prohibited
from helpers.db_connector import connection
from helpers.logger import logger
from helpers.namer import get_nick, get_chat_name

bot_response = None

rebukes = ["This is not the expected behaviour", "I don't want you to talk like that", "Expand your vocabulary now",
           "Bad language is not allowed okay", "See this is not my policy", "This is not a fruitful conversation",
           "This language is embarrassingassing to me like basically"]

responses1 = ["I am so sowry", "I don't want to talk like that", "it is embarrassing to me like basically",
              "it's not to trouble you like you say", "go for the worksheet", "it's not that hard"]

responses2 = ["it will be fruitful", "you will benefit", "that is the expected behaviour",
              "now you are on the track like", "now class is in the flow like", "don't press the jockey",
              "aim to hit the tarjit"]

JJ_RB = ["like you say", "like you speak"]  # For Adjectives or Adverbs


def shanifier(update: Update, context: CallbackContext, is_group: bool = False, the_id=None) -> None:
    user = update.message.from_user
    full_name = user.full_name
    bot_username = context.bot.name  # Bot username with @
    today = update.message.date
    org_text = update.message.text
    chat_id = update.effective_chat.id

    flag = 0  # To check if a modal is present in the sentence
    lydcount = 0  # Counts the number of times "like you do" has been added
    JJ_RBcount = 0  # Counts the number of times a phrase from JJ_RB has been added
    temp = 0

    name = get_nick(update, context)

    add_update_records(update, context)

    context.bot.send_chat_action(chat_id=chat_id, action='typing')  # Sends 'typing...' status for 6 sec

    if bot_username in org_text:  # Sends response if bot is @'ed in group
        msg_text = re.sub(rf"(\s*){bot_username}(\s*)", ' ', org_text)  # Remove mention from text so response is better
        the_id = update.message.message_id
    else:
        msg_text = org_text

    reply_to, bot_msg, user_msg = get_response(update, text=msg_text)

    if not is_group:
        shanisirbot.learn_response(user_msg, bot_response)
        chat_type = "(PRIVATE)"

    else:
        chat_type = f"(GROUP: {update.effective_chat.title})"

    punctuation = r"""!"#$%&'()*+,-./:;<=>?@[\]^_`{|}~"""
    bot_msg = ''.join(c for c in bot_msg if c not in punctuation)
    blob = TextBlob(bot_msg)
    cleaned = blob.words  # Returns list with no punctuation marks

    if len(cleaned) < 20:
        lydlim = 1  # to limit the number of times we add
        JJ_RBlim = 1  # lyd and JJ_RB
    else:
        lydlim = len(cleaned) // 20
        JJ_RBlim = len(cleaned) // 20

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
            cleaned.append(r.choice(responses1))
        else:
            cleaned.append(r.choice(responses2))
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

    shanitext = ' '.join(cleaned)
    shanitext = shanitext[0].upper() + shanitext[1:]

    inp = f"UTC+0 {today} {chat_type} {reply_to} {full_name} ({user.username}) SAID: {msg_text}\n"
    out = shanitext

    context.bot.send_message(chat_id=chat_id, text=out, reply_to_message_id=the_id)  # Sends message
    logger(message=f"\nThe input by {full_name} to the bot in {get_chat_name(update)} was:\n{msg_text}"
                   f"\n\n\nThe output by the bot was:\n{out}")

    with open("files/interactions.txt", "a") as f1:
        f1.write(emoji.demojize(inp))
        f1.write(f"BOT REPLY: {emoji.demojize(out)}\n\n")


def reply(update: Update, context: CallbackContext) -> None:
    text = update.message.text
    if update.message.reply_to_message.from_user.username == context.bot.username:  # If the reply is to a bot:
        if not (text.startswith('!r') or text.endswith('!r')):  # Don't reply if this is prepended or appended.
            logger(message=f"Bot received a reply from {update.effective_user.first_name} in "
                           f"{update.effective_chat.title}.")
            shanifier(update, context, is_group=True, the_id=update.message.message_id)

    elif context.bot.name in text:
        shanifier(update, context, is_group=True, the_id=update.message.message_id)


def group(update: Update, context: CallbackContext) -> None:
    """Checks for profanity in messages and responds to that."""

    chat_id = update.effective_chat.id
    text = update.message.text

    if any(bad_word in text.lower().split() for bad_word in prohibited):

        query = f"SELECT PROFANE_PROB FROM CHAT_SETTINGS WHERE CHAT_ID={chat_id};"
        true = connection(query, update)
        logger(message=f"The query executed on the database was:\n{query}\nand the result was:\n{true=}")

        false = 1 - true

        if r.choices([0, 1], weights=[false, true])[0]:  # Probabilities are 0.8 - False, 0.2 - True by default.
            name = get_nick(update, context)

            out = f"{r.choice(rebukes)} {name}"
            context.bot.send_message(chat_id=chat_id, text=out,
                                     reply_to_message_id=update.message.message_id)  # Sends message
            logger(message=f"{update.effective_user.first_name} used profane language in {get_chat_name(update)}."
                           f"\nThe rebuke by the bot was: '{out}'.")

    elif context.bot.name in text:
        shanifier(update, context, is_group=True, the_id=update.message.message_id)


def get_response(update: Update, text: str) -> (str, str, str):
    global bot_response

    if bot_response is None:
        search_in_response_text = None
    else:
        search_in_response_text = get_tags(bot_response.text)

    user_msg = chatterbot.conversation.Statement(text=text, search_text=get_tags(text), in_response_to=bot_response,
                                                 search_in_response_to=search_in_response_text)

    # If the user's message is a reply to a message
    if update.message.reply_to_message is not None:
        reply_text = update.message.reply_to_message.text
        if reply_text is not None:
            bot_response = chatterbot.conversation.Statement(text=reply_text, search_text=get_tags(reply_text))
            user_msg = chatterbot.conversation.Statement(text=text, search_text=get_tags(text),
                                                         in_response_to=bot_response,
                                                         search_in_response_to=get_tags(reply_text))

    reply_to = f"(REPLY TO [{user_msg.in_response_to}])"

    bot_response = shanisirbot.get_response(user_msg.text)

    if hasattr(bot_response, 'text'):
        bot_msg = bot_response.text
    else:
        bot_msg = 'Hello'

    return reply_to, bot_msg, user_msg


def add_update_records(update: Update, context: CallbackContext) -> None:
    chat_id = update.effective_chat.id
    user = update.message.from_user
    full_name = user.full_name
    username = user.username

    # Checks if your username or fullname or chat id is present in our records. If not, adds them.
    if 'username' not in context.user_data:
        context.user_data['username'] = [username]

    elif username != context.user_data['username'][-1]:
        context.user_data['username'].append(username)
        logger(message=f"{full_name} changed their username to: {username}.")

    if 'full_name' not in context.user_data:
        context.user_data['full_name'] = [full_name]

    elif full_name != context.user_data['full_name'][-1]:
        context.user_data['full_name'].append(full_name)
        logger(message=f"{username} changed their full name to: {full_name}.")

    if "chat_ids" not in context.chat_data:
        context.chat_data["chat_ids"] = [chat_id]
        logger(message=f"{full_name} is talking to the bot for the first time.")

    elif chat_id not in context.chat_data['chat_ids']:  # Gets chat id of the user in which they have talked to the bot
        context.chat_data['chat_ids'].append(chat_id)

    context.dispatcher.persistence.update_user_data(user.id, context.user_data)
    context.dispatcher.persistence.update_chat_data(chat_id, context.chat_data)
