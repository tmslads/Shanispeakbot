import logging

from telegram import (KeyboardButton, ReplyKeyboardMarkup, ReplyKeyboardRemove, InlineKeyboardMarkup,
                      InlineKeyboardButton, Update)
from telegram.ext import CallbackContext
from telegram.utils.helpers import create_deep_linked_url

from helpers.namer import get_nick, get_chat_name

# This is the main menu. Shown when /tell is invoked.
logging.basicConfig(format='%(asctime)s - %(module)s - %(levelname)s - %(lineno)d - %(message)s', level=logging.INFO)

keyboard = [[KeyboardButton(text="Birthday"), KeyboardButton(text="Nickname")],
            [KeyboardButton(text="Nothing")]]

markup = ReplyKeyboardMarkup(keyboard=keyboard, one_time_keyboard=True, selective=True)

CHOICE = 0


def initiate(update: Update, context: CallbackContext) -> int:  # Entry_point

    chat = update.effective_chat
    first_name = update.effective_user.first_name

    if chat.type != "private":

        link = create_deep_linked_url(bot_username=context.bot.username, payload="tell")
        button = [[InlineKeyboardButton(text="Let's go like you say!", url=link)]]
        tell_markup = InlineKeyboardMarkup(button)

        context.bot.send_message(chat_id=chat.id,
                                 text="Just come to another chat I want to talk to you like you say",
                                 reply_markup=tell_markup)

        logging.info(f"\n{first_name} just tried using /tell in a {chat.type}. "
                     f"A message telling them to use it private was sent.\n\n")

        return -1

    name = get_nick(update, context)

    context.bot.send_message(chat_id=chat.id,
                             text=f'What do you want to tell me {name}? Type /cancel anytime to switch me off',
                             reply_to_message_id=update.message.message_id, reply_markup=markup)

    logging.info(f"\n{first_name} just used /tell in {get_chat_name(update)}.\n\n")

    return CHOICE


def leave(update: Update, context: CallbackContext) -> int:
    name = get_nick(update, context)

    context.bot.send_message(chat_id=update.effective_chat.id,
                             text=f'Bye {name}, sit and solve the past papers like you say, I want to put a test okay?',
                             reply_to_message_id=update.message.message_id,
                             reply_markup=ReplyKeyboardRemove(selective=True))

    return -1


def timedout(update: Update, context: CallbackContext) -> None:
    context.bot.send_message(chat_id=update.effective_chat.id,
                             text="Ok I am fine being seenzoned",
                             reply_to_message_id=update.message.message_id,
                             reply_markup=ReplyKeyboardRemove(selective=True))

    logging.info(f"\n{update.effective_user.first_name} just timed out while using /tell.\n\n")
