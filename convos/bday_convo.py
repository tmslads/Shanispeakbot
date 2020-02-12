# birthday function conversation-

import datetime

from telegram import ForceReply
from telegram import KeyboardButton
from telegram import ReplyKeyboardMarkup

from gcalendar import formatter
from start import markup, CHOICE

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

    if 'birthday' not in context.user_data:
        context.bot.send_message(chat_id=update.effective_chat.id,
                                 text="I don't know your birthday like you say. When? \nEnter your DOB as: YYYY-MM-DD",
                                 reply_to_message_id=update.message.message_id,
                                 reply_markup=ForceReply(selective=True)
                                 )
        print("Not present")
        return INPUT

    else:
        bday_keyboard = [
            [KeyboardButton(text="Update my birthday sir"), KeyboardButton(text="Forget my birthday sir")],
            [KeyboardButton(text="No, thank you sir")]]

        bday_markup = ReplyKeyboardMarkup(keyboard=bday_keyboard, one_time_keyboard=True)
        print("user id present, bday present")

        b_date = context.user_data['birthday']
        context.bot.send_message(chat_id=update.effective_chat.id,
                                 text=f"Your birthday is on"
                                      f" {formatter(b_date, format_style='DD/MM')} and"
                                      f" you are {age_cal(b_date)} years old. Would you like to update or remove it?",
                                 reply_to_message_id=update.message.message_id,
                                 reply_markup=bday_markup
                                 )
        print("Returning modify..")
        return MODIFY


def bday_add_or_update(update, context):  # INPUT
    bday_date = update.message.text

    try:
        dt_obj = datetime.datetime.strptime(bday_date, "%Y-%m-%d")

    except Exception as e:
        print(e)
        wrong(update, context)

    else:
        name = nicknamer(update, context)

        if context.user_data:
            print("id was present")

        else:
            print("id wasn't present. Adding")

        if 'birthday' in context.user_data:
            print("Birthday present")
            if isinstance(context.user_data['birthday'], datetime.datetime):
                print("Birthday present, updating...")
                print("Old bday ", context.user_data['birthday'])
                print("Updated bday ", dt_obj)
        context.user_data['birthday'] = dt_obj
        for k, v in context.user_data.items():
            print(k, v)
        context.bot.send_message(chat_id=update.effective_chat.id,
                                 text=f"Ok {name}, I'll remember your birthday like you say.",
                                 reply_markup=markup)
        return CHOICE


def bday_mod(update, context):  # MODIFY
    name = nicknamer(update, context)

    print("in modify state")

    context.bot.send_message(chat_id=update.effective_chat.id, text=f"{name}, I know your birthday yes? If it is"
                                                                    f" wrong you can come and tell me the correct"
                                                                    f" one okay?"
                                                                    f"\nEnter your DOB as: YYYY-MM-DD",
                             reply_to_message_id=update.message.message_id,
                             reply_markup=ForceReply(selective=True))
    return INPUT


def bday_del(update, context):  # MODIFY
    name = nicknamer(update, context)

    context.bot.send_message(chat_id=update.effective_chat.id, text=f"Ok {name}, I forgot your birthday",
                             reply_to_message_id=update.message.message_id, reply_markup=markup)

    try:
        del context.user_data['birthday']
    except KeyError:
        print("User not found!")
    finally:
        return CHOICE


def age_cal(date: datetime.datetime):
    today = datetime.datetime.utcnow()
    age = today - date
    return age.days // 365


def reject(update, context):
    context.bot.send_message(chat_id=update.effective_chat.id, text=f"Ok, what you want to do like?",
                             reply_to_message_id=update.message.message_id, reply_markup=markup)

    return CHOICE


def wrong(update, context):
    context.bot.send_message(chat_id=update.effective_chat.id,
                             text=f"This is not correct. Aim to hit the tarjit.\nEnter your DOB as: YYYY-MM-DD",
                             reply_markup=ForceReply(selective=True),
                             reply_to_message_id=update.message.message_id)
    return INPUT
