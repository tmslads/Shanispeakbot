# birthday function conversation-

import datetime

from telegram import ForceReply
from telegram import KeyboardButton
from telegram import ReplyKeyboardMarkup

from gcalendar import formatter
from .start import markup, CHOICE

INPUT, MODIFY = range(1, 3)


def nicknamer(update, context):
    try:
        name = context.user_data['nickname'][-1]
    except (KeyError, IndexError):
        context.user_data['nickname'] = []
        context.user_data['nickname'].append(update.message.from_user.first_name)
    finally:
        return context.user_data['nickname'][-1]


def bday(update, context):  # CHOICE
    """Asks user for their birthday if it is not known, else gives options on what to do with them."""

    # Asks user for birthday if we don't have it stored.
    if 'birthday' not in context.user_data:
        context.bot.send_message(chat_id=update.effective_chat.id,
                                 text="I don't know your birthday like you say. When? \nEnter your DOB as: YYYY-MM-DD",
                                 reply_to_message_id=update.message.message_id,
                                 reply_markup=ForceReply(selective=True)
                                 )
        return INPUT

    else:
        # Gives options for users by asking them what to do with their birthdays.
        bday_keyboard = [
            [KeyboardButton(text="Update my birthday sir"), KeyboardButton(text="Forget my birthday sir")],
            [KeyboardButton(text="No, thank you sir")]]

        bday_markup = ReplyKeyboardMarkup(keyboard=bday_keyboard, one_time_keyboard=True)

        b_date = context.user_data['birthday']
        context.bot.send_message(chat_id=update.effective_chat.id,
                                 text=f"Your birthday is on"
                                      f" {formatter(b_date, format_style='DD/MM')} and"
                                      f" you are {age_cal(b_date)} years old. Would you like to update or remove it?",
                                 reply_to_message_id=update.message.message_id,
                                 reply_markup=bday_markup
                                 )
        return MODIFY


def bday_add_or_update(update, context):  # INPUT
    """Changes or adds your birthday into our records."""

    bday_date = update.message.text

    try:
        dt_obj = datetime.datetime.strptime(bday_date, "%Y-%m-%d")

    except Exception as e:  # If user didn't enter birthday in the right format
        print(e)
        wrong(update, context)  # Asks for a valid input

    else:
        name = nicknamer(update, context)
        context.user_data['birthday'] = dt_obj

        context.bot.send_message(chat_id=update.effective_chat.id,
                                 text=f"Ok {name}, I'll remember your birthday like you say.",
                                 reply_markup=markup)
        return CHOICE


def bday_mod(update, context):  # MODIFY
    """Asks user for input so we can update their birthday"""

    name = nicknamer(update, context)

    context.bot.send_message(chat_id=update.effective_chat.id, text=f"{name}, I know your birthday yes? If it is"
                                                                    f" wrong you can come and tell me the correct"
                                                                    f" one okay?"
                                                                    f"\nEnter your DOB as: YYYY-MM-DD",
                             reply_to_message_id=update.message.message_id,
                             reply_markup=ForceReply(selective=True))
    return INPUT


def bday_del(update, context):  # MODIFY
    """Deletes birthday from our records. Then goes back to main menu."""

    name = nicknamer(update, context)

    context.bot.send_message(chat_id=update.effective_chat.id, text=f"Ok {name}, I forgot your birthday",
                             reply_to_message_id=update.message.message_id, reply_markup=markup)

    del context.user_data['birthday']
    return CHOICE


def age_cal(date: datetime.datetime):
    """Returns your age based on your birth date."""

    today = datetime.datetime.utcnow()
    age = today - date
    return age.days // 365


def reject(update, context):  # fallback
    """When user cancels current operation. Goes back to main menu."""

    context.bot.send_message(chat_id=update.effective_chat.id, text=f"Ok, what you want to do like?",
                             reply_to_message_id=update.message.message_id, reply_markup=markup)

    return CHOICE


def wrong(update, context):  # fallback
    """Asks user to enter his birthdate correctly."""

    context.bot.send_message(chat_id=update.effective_chat.id,
                             text=f"This is not correct. Aim to hit the tarjit.\nEnter your DOB as: YYYY-MM-DD",
                             reply_markup=ForceReply(selective=True),
                             reply_to_message_id=update.message.message_id)
    return INPUT
