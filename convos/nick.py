import logging

from telegram import ForceReply, Update
from telegram import KeyboardButton
from telegram import ReplyKeyboardMarkup
from telegram.ext import CallbackContext

from commands import prohibited
from .start import markup, CHOICE

SET_NICK, MODIFY_NICK = range(3, 5)

logging.basicConfig(format='%(asctime)s - %(module)s - %(levelname)s - %(lineno)d - %(message)s', level=logging.INFO)


def nick(update: Update, context: CallbackContext) -> int:
    """
    Checks if nickname is set or not, if set, then gives options on what to do with them. Else will ask to set
    a nickname.
    """
    name = update.message.from_user.first_name
    chat_id = update.effective_chat.id
    msg_id = update.message.message_id

    if 'nickname' not in context.user_data or context.user_data['nickname'][-1] == name:
        context.bot.send_message(chat_id=chat_id,
                                 text="What is your uhh.. what you say like... nickname?",
                                 reply_to_message_id=msg_id, reply_markup=ForceReply(selective=True))

        return SET_NICK

    else:
        nick_kb = [[KeyboardButton("Change nickname"), KeyboardButton("Remove nickname")],
                   [KeyboardButton("Back")]]

        nick_markup = ReplyKeyboardMarkup(nick_kb, one_time_keyboard=True, selective=True)
        nick_name = context.user_data["nickname"][-1]
        context.bot.send_message(chat_id=chat_id,
                                 text=f"Hi {nick_name}, what you want to do like?", reply_markup=nick_markup,
                                 reply_to_message_id=msg_id)

        return MODIFY_NICK


def del_nick(update: Update, context: CallbackContext) -> int:  # MODIFY_NICK
    """Deletes nickname (i.e.) sets it to your first name."""

    name = update.message.from_user.first_name

    context.user_data['nickname'].append(name)
    context.bot.send_message(chat_id=update.effective_chat.id,
                             text=f"I'm forgetting your nic.. {name}",
                             reply_to_message_id=update.message.message_id,
                             reply_markup=markup)

    logging.info(f"\n{name} just deleted their nickname.\n\n")

    return CHOICE


def edit_nick(update: Update, context: CallbackContext) -> int:  # MODIFY_NICK
    """Asks for new nickname."""

    context.bot.send_message(chat_id=update.effective_chat.id,
                             text="Tell me your new nickname like you say",
                             reply_to_message_id=update.message.message_id, reply_markup=ForceReply(selective=True))
    return SET_NICK


def add_edit_nick(update: Update, context: CallbackContext) -> int:  # SET_NICK
    """Adds or updates your nickname. Then goes back to main menu."""

    chat_id = update.effective_chat.id
    msg_id = update.message.message_id

    if 'nickname' not in context.user_data:
        context.user_data['nickname'] = []

    if any(bad_word in update.message.text.lower().split() for bad_word in prohibited):
        context.bot.send_message(chat_id=chat_id, reply_markup=ForceReply(selective=True), reply_to_message_id=msg_id,
                                 text="See this language is embarrassing to me ok. I'm giving you one more chance "
                                      "that's it.")
        return SET_NICK

    else:
        context.user_data['nickname'].append(update.message.text)
        nicky = context.user_data['nickname'][-1]

        context.bot.send_message(chat_id=chat_id, text=f"Hi {nicky} what you're doing like", reply_to_message_id=msg_id,
                                 reply_markup=markup)
        logging.info(f"\n{update.effective_user.first_name} just changed their nickname to {nicky}.\n\n")

        return CHOICE


def back(update: Update, context: CallbackContext) -> int:  # MODIFY_NICK
    """Goes back to main menu."""

    context.bot.send_message(chat_id=update.effective_chat.id,
                             text=f"What you want?",
                             reply_to_message_id=update.message.message_id,
                             reply_markup=markup)
    return CHOICE
