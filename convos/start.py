from telegram import KeyboardButton, ReplyKeyboardMarkup, ReplyKeyboardRemove

from .namer import nicknamer

# This is the main menu. Shown when /tell is invoked.

keyboard = [
    [KeyboardButton(text="Birthday"), KeyboardButton(text="Nickname")],
    [KeyboardButton(text="Nothing")]
]
markup = ReplyKeyboardMarkup(keyboard=keyboard, one_time_keyboard=True, selective=True)

CHOICE = range(1)


def initiate(update, context):  # Entry_point
    name = nicknamer(update, context)

    context.bot.send_message(chat_id=update.effective_chat.id,
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
