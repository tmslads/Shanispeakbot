# birthday function conversation-

import datetime

from telegram import ForceReply
from telegram import KeyboardButton
from telegram import ReplyKeyboardMarkup

from gcalendar import formatter
from start import markup, CHOICE

INPUT, MODIFY = range(2)


def bday(update, context):  # CHOICE
    user_id = update.message.from_user.id

    if user_id not in context.user_data['birthdays']:
        update.message.reply_text("I don't know your birthday like you say. When? \nEnter your DOB as: YYYY-MM-DD")
        return INPUT

    else:
        bday_keyboard = [
            [KeyboardButton(text="Update my birthday sir"), KeyboardButton(text="Forget my birthday sir")],
            [KeyboardButton(text="No, thank you sir")]]

        bday_markup = ReplyKeyboardMarkup(keyboard=bday_keyboard, one_time_keyboard=True)

        context.bot.send_message(chat_id=update.effective_chat.id,
                                 text=f"Your birthday is on"
                                      f" {formatter(context.user_data['birthdays'][user_id], format_style='DD/MM')}."
                                      f" Would you like to update or remove it?",
                                 reply_to_message_id=update.message.message_id,
                                 reply_markup=bday_markup
                                 )

        return MODIFY


def bday_add_or_update(update, context):  # INPUT
    bday_date = update.message.text

    try:
        dt_obj = datetime.datetime.strptime(bday_date, "%Y-%m-%d")

    except Exception as e:
        print(e)

    else:
        user_id = update.message.from_user.id
        name = update.message.from_user.first_name
        context.user_data['birthdays'][user_id] = dt_obj
        context.bot.send_message(chat_id=update.effective_chat.id,
                                 text=f"Ok {name}, I'll remember your birthday like you say.",
                                 reply_markup=markup)
        return CHOICE


def bday_mod(update, context):  # MODIFY
    user_id = update.message.from_user.id
    name = update.message.from_user.first_name

    context.bot.send_message(chat_id=update.effective_chat.id, text=f"{name}, I know your birthday yes? If it is"
                                                                    f" wrong you can come and tell me the correct"
                                                                    f" one okay?"
                                                                    f"\nEnter your DOB as: YYYY-MM-DD",
                             reply_to_message_id=update.message.message_id,
                             reply_markup=ForceReply(force_reply=True, selective=True))
    return INPUT


def bday_del(update, context):  # MODIFY
    user_id = update.message.from_user.id
    name = update.message.from_user.first_name

    context.bot.send_message(chat_id=update.effective_chat.id, text=f"Ok {name}, I forgot your birthday",
                             reply_to_message_id=update.message.message_id, reply_markup=markup)

    try:
        del context.user_data['birthdays'][user_id]
    except KeyError:
        print("User not found!")
    finally:
        return CHOICE


def reject(update, context):
    context.bot.send_message(chat_id=update.effective_chat.id, text=f"Ok, what you want to do like?",
                             reply_to_message_id=update.message.message_id, reply_markup=markup)

    return CHOICE


def wrong(update, context):
    context.bot.send_message(chat_id=update.effective_chat.id,
                             text=f"This is not correct. Aim to hit the tarjit.\nEnter your DOB as: YYYY-MM-DD",
                             reply_markup=ForceReply(force_reply=True, selective=True),
                             reply_to_message_id=update.message.message_id)
    return INPUT
