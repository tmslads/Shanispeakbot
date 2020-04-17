# birthday function conversation-
import datetime
import logging

from telegram import ForceReply, Update
from telegram import KeyboardButton
from telegram import ReplyKeyboardMarkup
from telegram.ext import CallbackContext

from helpers.namer import get_nick
from online.gcalendar import formatter
from .start import markup, CHOICE

INPUT, MODIFY = range(1, 3)

logging.basicConfig(format='%(asctime)s - %(module)s - %(levelname)s - %(lineno)d - %(message)s', level=logging.INFO)


def bday(update: Update, context: CallbackContext) -> int:  # CHOICE
    """Asks user for their birthday if it is not known, else gives options on what to do with them."""

    chat_id = update.effective_chat.id
    msg_id = update.message.message_id

    # Asks user for birthday if we don't have it stored.
    if 'birthday' not in context.user_data:
        context.bot.send_message(chat_id=chat_id,
                                 text="I don't know your birthday like you say. When? \nEnter your DOB as: YYYY-MM-DD",
                                 reply_to_message_id=msg_id,
                                 reply_markup=ForceReply(selective=True)
                                 )
        return INPUT

    else:
        # Gives options for users by asking them what to do with their birthdays.
        bday_keyboard = [
            [KeyboardButton(text="Update my birthday sir"), KeyboardButton(text="Forget my birthday sir")],
            [KeyboardButton(text="No, thank you sir")]]

        bday_markup = ReplyKeyboardMarkup(keyboard=bday_keyboard, one_time_keyboard=True, selective=True)

        b_date = context.user_data['birthday']
        context.bot.send_message(chat_id=chat_id,
                                 text=f"Your birthday is on"
                                      f" {formatter(b_date, format_style='DD/MM')} and"
                                      f" you are {age_cal(b_date)} years old. Would you like to update or remove it?",
                                 reply_to_message_id=msg_id,
                                 reply_markup=bday_markup
                                 )
        return MODIFY


def bday_add_or_update(update: Update, context: CallbackContext) -> int:  # INPUT
    """Changes or adds your birthday into our records."""

    bday_date = update.message.text

    try:
        dt_obj = datetime.datetime.strptime(bday_date, "%Y-%m-%d")

    except Exception as e:  # If user didn't enter birthday in the right format
        logging.exception(f"\nThe traceback is: {e}\n\n")
        wrong(update, context)  # Asks for a valid input

    else:
        name = get_nick(update, context)
        context.user_data['birthday'] = dt_obj

        context.bot.send_message(chat_id=update.effective_chat.id,
                                 text=f"Ok {name}, I'll remember your birthday like you say.",
                                 reply_markup=markup)

        logging.info(f"\n{update.effective_user.first_name} just changed their birthday to {bday_date}.\n\n")

        return CHOICE


def bday_mod(update: Update, context: CallbackContext) -> int:  # MODIFY
    """Asks user for input so we can update their birthday"""

    name = get_nick(update, context)

    context.bot.send_message(chat_id=update.effective_chat.id, text=f"{name}, I know your birthday yes? If it is"
                                                                    f" wrong you can come and tell me the correct"
                                                                    f" one okay?"
                                                                    f"\nEnter your DOB as: YYYY-MM-DD",
                             reply_to_message_id=update.message.message_id,
                             reply_markup=ForceReply(selective=True))
    return INPUT


def bday_del(update: Update, context: CallbackContext) -> int:  # MODIFY
    """Deletes birthday from our records. Then goes back to main menu."""

    name = get_nick(update, context)

    context.bot.send_message(chat_id=update.effective_chat.id, text=f"Ok {name}, I forgot your birthday",
                             reply_to_message_id=update.message.message_id, reply_markup=markup)

    logging.info(f"\n{update.effective_user.first_name} just deleted their birthday.\n\n")

    del context.user_data['birthday']
    return CHOICE


def age_cal(date: datetime.datetime) -> int:
    """Returns your age based on your birth date."""

    today = datetime.datetime.utcnow()
    age = today - date
    return age.days // 365


def reject(update: Update, context: CallbackContext) -> int:  # fallback
    """When user cancels current operation. Goes back to main menu."""

    context.bot.send_message(chat_id=update.effective_chat.id, text=f"Ok, what you want to do like?",
                             reply_to_message_id=update.message.message_id, reply_markup=markup)

    return CHOICE


def wrong(update: Update, context: CallbackContext) -> int:  # INPUT
    """Asks user to enter his birthdate correctly."""

    context.bot.send_message(chat_id=update.effective_chat.id,
                             text=f"This is not correct. Aim to hit the tarjit.\nEnter your DOB as: YYYY-MM-DD",
                             reply_markup=ForceReply(selective=True),
                             reply_to_message_id=update.message.message_id)
    return INPUT
