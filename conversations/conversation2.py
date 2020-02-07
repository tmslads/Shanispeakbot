# /tell function conversation-

from telegram import KeyboardButton
from telegram import ReplyKeyboardMarkup
import datetime
CHOICE, INPUT = range(2)


class UserChoices(object):
    @staticmethod
    def bday(update, context):
        user_id = update.message.from_user.id
        if 'birthdays' not in context.user_data:
            context.user_data['birthdays'] = {}

        if user_id not in context.user_data['birthdays']:
            update.message.reply_text("I don't know your birthday like you say. When? \nEnter as: YYYY-MM-DD")
            return INPUT

        print(context.user_data)

        if user_id in context.user_data:
            keyboard = [[KeyboardButton(text="Yes sir"), KeyboardButton(text="No thank you sir")]]
            markup = ReplyKeyboardMarkup(keyboard=keyboard, one_time_keyboard=True)

            context.bot.send_message(chat_id=update.effective_chat.id,
                                     text=f"Your birthday is on {context.user_data[user_id]}. Would you like to"
                                          f"update it?",
                                     reply_to_message_id=update.message.message_id,
                                     reply_markup=markup
                                     )

        # return -1

    @staticmethod
    def nick(update, context):
        pass


def initiate(update, context):
    name = update.message.from_user.first_name

    keyboard = [
        [KeyboardButton(text="Birthday"), KeyboardButton(text="Secret")],
        [KeyboardButton(text="Nickname"), KeyboardButton(text="Other")]
    ]

    markup = ReplyKeyboardMarkup(keyboard=keyboard, one_time_keyboard=True)
    context.bot.send_message(chat_id=update.effective_chat.id, text=f'What do you want to tell me {name}?',
                             reply_to_message_id=update.message.message_id, reply_markup=markup)
    return CHOICE


def bday_add(update, context):
    bday_date = update.message.text

    try:
        dt_obj = datetime.datetime.strptime(bday_date, "%Y-%m-%d")

    except Exception as e:
        print(e)
        update.message.reply_text(f"This is not correct. Aim to hit the tarjit.\nEnter as: YYYY-MM-DD")
        return INPUT

    else:
        user_id = update.message.from_user.id
        name = update.message.from_user.first_name
        context.user_data['birthdays'][user_id] = dt_obj
        update.message.reply_text(f"Ok {name}, I'll remember your birthday like you say.")
        return CHOICE
