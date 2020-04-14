from telegram import (KeyboardButton, ReplyKeyboardMarkup, ReplyKeyboardRemove, InlineKeyboardMarkup,
                      InlineKeyboardButton)
from telegram.utils.helpers import create_deep_linked_url

from .namer import nicknamer

# This is the main menu. Shown when /tell is invoked.

keyboard = [
    [KeyboardButton(text="Birthday"), KeyboardButton(text="Nickname")],
    [KeyboardButton(text="Nothing")]
]
markup = ReplyKeyboardMarkup(keyboard=keyboard, one_time_keyboard=True, selective=True)

CHOICE = range(1)


def initiate(update, context):  # Entry_point

    chat_id = update.effective_chat.id
    if update.effective_chat.type != "private":

        link = create_deep_linked_url(bot_username="Ttessttingbot", payload="tell")
        button = [[InlineKeyboardButton(text="Let's go like you say!", url=link)]]
        tell_markup = InlineKeyboardMarkup(button)

        context.bot.send_message(chat_id=chat_id,
                                 text="Just come to another chat I want to talk to you like you say",
                                 reply_markup=tell_markup)
        return -1

    name = nicknamer(update, context)

    context.bot.send_message(chat_id=chat_id,
                             text=f'What do you want to tell me {name}? Type /cancel anytime to switch me off',
                             reply_to_message_id=update.message.message_id, reply_markup=markup)
    return CHOICE


def leave(update, context):
    name = nicknamer(update, context)

    context.bot.send_message(chat_id=update.effective_chat.id,
                             text=f'Bye {name}, sit and solve the past papers like you say, I want to put a test okay?',
                             reply_to_message_id=update.message.message_id,
                             reply_markup=ReplyKeyboardRemove(selective=True))

    return -1


def timedout(update, context):
    context.bot.send_message(chat_id=update.effective_chat.id,
                             text="Ok I am fine being seenzoned",
                             reply_to_message_id=update.message.message_id,
                             reply_markup=ReplyKeyboardRemove(selective=True))
