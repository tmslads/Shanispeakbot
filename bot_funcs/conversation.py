import random as r
import re

import chatterbot
import emoji
from telegram import Update
from telegram.ext import CallbackContext
import spacy

from chatbot import get_tags, shanisirbot
from bot_funcs.commands import prohibited
from helpers.db_connector import connection
from helpers.logger import logger
from helpers.namer import get_nick, get_chat_name

bot_response = None

rebukes = ("This is not the expected behaviour", "I don't want you to talk like that", "Expand your vocabulary now",
           "Bad language is not allowed okay", "See this is not my policy", "This is not a fruitful conversation",
           "This language is embarrassingassing to me like basically")

responses1 = ("I am so sowry", "I don't want to talk like that", "it is embarrassing to me like basically",
              "it's not to trouble you like you say", "go for the worksheet", "it's not that hard")

responses2 = ("it will be fruitful", "you will benefit", "that is the expected behaviour",
              "now you are on the track like", "now class is in the flow like", "don't press the jockey",
              "aim to hit the tarjit")

JJ_RB = ("like you say", "like you speak")  # For Adjectives or Adverbs


def shanifier(update: Update, context: CallbackContext, is_group: bool = False, the_id: int = None) -> None:
    """
    This function shanifies text using NLP (Natural Language Processing) and sends the resulting text to the
    respective chat. It also writes the input and output to a file. Only private chat responses are 'learned' by the
    bot for future use.

    Args:
        update (:obj:`Update`): Update object provided by Telegram.
        context (:obj:'CallbackContext`): CallbackContext passed in by Python Telegram Bot.
        is_group (:obj:`bool`, optional): Set to True, if received message is from a group. Default is `False`.
        the_id (:obj:`int`, int): The message_id of the message to reply to in a chat.
    """

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

    context.bot.send_chat_action(chat_id=chat_id, action='typing')  # Sends 'typing...' status for 5 sec

    if bot_username in org_text:  # Sends response if bot is @'ed in group
        msg_text = re.sub(rf"(\s*){bot_username}(\s*)", ' ', org_text)  # Remove mention from text so response is better
        the_id = update.message.message_id
    else:
        msg_text = org_text

    reply_to, bot_msg, user_msg = get_response(update, text=msg_text)

    if not is_group:
        shanisirbot.learn_response(user_msg, bot_response)  # Learn response if it's a private chat
        chat_type = "(PRIVATE)"  # for interactions.txt

    else:
        chat_type = f"(GROUP: {update.effective_chat.title})"

    nlp = spacy.load("en_core_web_sm")
    sentence = nlp(bot_msg)

    word_list = [word.text for word in sentence]  # Get words used in the sentence

    # Begin shanifying text-
    if len(word_list) < 20:
        lydlim = 1  # to limit the number of times we add
        JJ_RBlim = 1  # lyd and JJ_RB
    else:
        lydlim = len(word_list) // 20
        JJ_RBlim = len(word_list) // 20

    for index, word in enumerate(sentence):  # returns list of tuples which tells the POS
        if index - temp < 7:  # Do not add lad things too close to each other
            continue

        if word.tag_ == 'MD' and not flag:  # Modal
            word_list.insert(index + 1, "(if the laws of physics allow it)")
            flag = 1

        if word.tag_ in ('JJ', 'JJR', 'JJS', 'RB', 'RBR', 'RBS') and JJ_RBcount < JJ_RBlim:  # Adjective or Adverb
            word_list.insert(index + 1, r.choice(JJ_RB))
            JJ_RBcount += 1
            temp = index

        elif word.tag_ in ('VB', 'VBD', 'VBG', 'VBN', 'VBP', 'VBZ') and lydcount < lydlim:  # Verb
            word_list.insert(index + 1, "like you do")
            lydcount += 1
            temp = index

    if r.choice([0, 1]):
        if r.choice([0, 1]):
            word_list.append(r.choice(responses1 + responses2))
        word_list.insert(0, name)

    elif r.choice([0, 1]):
        if '?' in bot_msg:  # Insert name at beginning if it's a question
            word_list.insert(0, name.capitalize())
        else:
            word_list.append(f"{name}.")

    if len(word_list) < 5 and r.choice([0, 1]):  # Might run if input is too short
        word_list.append(r.choice(("*draws perfect circle*", " *scratches nose*")))

    if re.search('when|time', ' '.join(word_list), flags=re.IGNORECASE):
        word_list.append('decide a date')

    for word in update.message.text:
        if word in emoji.UNICODE_EMOJI:  # Checks if emoji is present in message
            word_list.append(r.choice(list(emoji.UNICODE_EMOJI)))  # Adds a random emoji

    # Text processing and replacing-
    shanitext = re.sub(r" (?=[.!,:;?])", '', ' '.join(word_list))  # Remove spaces before .!,:;? - Lookahead assertion
    shanitext = re.sub(r"(\s*)*(\w?)'", r"\1\2'", shanitext)  # Remove spaces before contractions (Let 's, ca n't, etc)
    shanitext = re.sub("(^|[.?!])\s*([a-zA-Z])", lambda p: p.group(0).upper(), shanitext)  # Capitalize letter after .?!
    shanitext = re.sub(f"[.] ({name})", r", \1", shanitext)  # Convert . into , if . is followed by name (usually @ end)

    shanitext = shanitext[0].upper() + shanitext[1:]  # Make only first letter capital

    inp = f"UTC+0 {today} {chat_type} {reply_to} {full_name} ({user.username}) SAID: {msg_text}\n"
    out = shanitext

    context.bot.send_message(chat_id=chat_id, text=out, reply_to_message_id=the_id)  # Sends message to respective chat
    logger(message=f"\nThe input by {full_name} to the bot in {get_chat_name(update)} was:\n{msg_text}"
                   f"\n\n\nThe output by the bot was:\n{out}")

    with open("files/interactions.txt", "a") as f1:
        f1.write(emoji.demojize(inp))
        f1.write(f"BOT REPLY: {emoji.demojize(out)}\n\n")


def reply(update: Update, context: CallbackContext) -> None:
    """
    This function checks if the user is replying to a message of this bot in a group, if it is, it sends a reply
    to that person. Same behaviour applies for this bot mentions in replies (reply to anyone, not just this bot).
    """

    text = update.message.text
    if update.message.reply_to_message.from_user.username == context.bot.username:  # If the reply is to this bot:
        if not (text.startswith('!r') or text.endswith('!r')):  # Don't reply if this is prepended or appended.
            logger(message=f"Bot received a reply from {update.effective_user.first_name} in "
                           f"{update.effective_chat.title}.")
            shanifier(update, context, is_group=True, the_id=update.message.message_id)

    elif context.bot.name in text:
        shanifier(update, context, is_group=True, the_id=update.message.message_id)

    del text


def group(update: Update, context: CallbackContext) -> None:
    """
    Checks for profanity in messages and responds to that. Also checks if the bot was mentioned in the chat,
    if it was, replies to that message.
    """

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

    elif context.bot.name in text:  # If username was mentioned in group chat, reply to it.
        shanifier(update, context, is_group=True, the_id=update.message.message_id)

    del chat_id, text


def get_response(update: Update, text: str) -> (str, str, str):
    """
    This function fetches an appropriate response (hopefully) using the chatterbot module. Responses are fetched from a
    database based on the text provided.

    Args:
        update (:obj:`Update`): Update object provided by Telegram.
        text (:obj:`str`): The text message to get a response from. Eg: 'Hi', 'How was your day?', etc.

    Returns:
        reply_to (:obj:`str`): The message to which the response is a reply to. Used only for interactions.txt
        bot_msg (:obj:`str`): The response of the bot to the message sent by the user.
        user_msg (:obj:`str`): Message sent by the user to the bot.
    """

    global bot_response

    if bot_response is None:  # Will be None when bot is first started
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
    """
    This function adds or updates the user's information (username, full name, user id) to the chat_data and
    user_data objects.
    """

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

    if "chat_name" not in context.chat_data:
        context.chat_data['chat_name'] = get_chat_name(update)

    context.dispatcher.persistence.flush()
