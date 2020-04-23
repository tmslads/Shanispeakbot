from telegram import (KeyboardButton, ReplyKeyboardMarkup, ReplyKeyboardRemove, InlineKeyboardMarkup,
                      InlineKeyboardButton, Update)
from telegram.ext import CallbackContext
from telegram.utils.helpers import create_deep_linked_url

from helpers.logger import logger
from helpers.namer import get_nick

# This is the main menu. Shown when /tell is invoked.

keyboard = [[KeyboardButton(text="Birthday"), KeyboardButton(text="Nickname")], [KeyboardButton(text="Nothing")]]

markup = ReplyKeyboardMarkup(keyboard=keyboard, one_time_keyboard=True, selective=True)

CHOICE = 0


def initiate(update: Update, context: CallbackContext) -> int:  # Entry_point

    chat = update.effective_chat
    first_name = update.effective_user.first_name

    if chat.type != "private":
        link = create_deep_linked_url(bot_username=context.bot.username, payload="tell")
        button = [[InlineKeyboardButton(text="Let's go like you say!", url=link)]]
        tell_markup = InlineKeyboardMarkup(button)

        context.bot.send_message(chat_id=chat.id, text="Just come to another chat I want to talk to you like you say",
                                 reply_markup=tell_markup)

        logger(message=f"{first_name} just tried using /tell in a {chat.type}. "
                       f"A message telling them to use it private was sent.")

        return -1

    name = get_nick(update, context)

    context.bot.send_message(chat_id=chat.id,
                             text=f'What do you want to tell me {name}? Type /cancel anytime to switch me off',
                             reply_to_message_id=update.message.message_id, reply_markup=markup)

    logger(message=f"/tell", update=update, command=True)

    return CHOICE


def leave(update: Update, context: CallbackContext) -> int:
    name = get_nick(update, context)

    context.bot.send_message(chat_id=update.effective_chat.id,
                             text=f'Bye {name}, sit and solve the past papers like you say, I want to put a test okay?',
                             reply_to_message_id=update.message.message_id,
                             reply_markup=ReplyKeyboardRemove(selective=True))

    return -1


def timedout(update: Update, context: CallbackContext) -> None:
    context.bot.send_message(chat_id=update.effective_chat.id, text="Ok I am fine being seenzoned",
                             reply_to_message_id=update.message.message_id,
                             reply_markup=ReplyKeyboardRemove(selective=True))

    logger(message=f"{update.effective_user.first_name} just timed out while using /tell.")
