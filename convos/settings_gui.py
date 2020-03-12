import sqlite3

from telegram import (InlineKeyboardMarkup, InlineKeyboardButton)
from telegram import error

from constants import samir, harshil, sql_table

CURRENT_SETTINGS, UPDATED, SAVE = range(3)

msg = None

settings = []
columns = ["media_reactions", "profanity_check", "morning_msgs"]

buttons = [[InlineKeyboardButton(text="Media reactions", callback_data=str(0))],
           [InlineKeyboardButton(text="Profanity checker", callback_data=str(1))],
           [InlineKeyboardButton(text="Morning quote", callback_data=str(2))],
           [InlineKeyboardButton(text="Save changes", callback_data="SAVE")]]
setting_markup = InlineKeyboardMarkup(buttons)


def start(update, context):
    global settings, conn, c

    chat_id = update.effective_chat.id
    user_id = update.message.from_user.id
    try:
        admins = context.bot.get_chat_administrators(chat_id=chat_id)
    except error.BadRequest:  # When it is a private chat
        pass
    else:
        for admin in admins:
            if user_id in (samir, harshil) or admin.user.id == user_id:
                print(user_id, update.message.from_user.first_name)
                break
        else:
            context.bot.send_message(chat_id=chat_id,
                                     text=r"This command can only be used by the chat's admin(s) / owner.",
                                     reply_to_message_id=update.message.message_id)
            return -1

    conn = sqlite3.connect('./files/bot_settings.db')
    c = conn.cursor()
    name = namer(update, context)

    c.executescript(sql_table)
    conn.commit()

    c.execute(f"SELECT EXISTS(SELECT * FROM CHAT_SETTINGS WHERE chat_id = {chat_id});")  # Returns 0 if doesn't exist
    result = c.fetchone()
    print(result)
    print(chat_id)
    if not result[0]:
        print("in if condition")

        c.execute("PRAGMA table_info(CHAT_SETTINGS);")
        print(c.fetchall())

        c.execute("SELECT * FROM CHAT_SETTINGS;")
        print(c.fetchall())

        c.execute(f"INSERT INTO CHAT_SETTINGS VALUES({chat_id},'{name}',True,True,False);")
        conn.commit()
        c.execute(f"SELECT * FROM CHAT_SETTINGS WHERE chat_id = {chat_id};")
        print(c.fetchall())

    c.execute(f"SELECT * FROM CHAT_SETTINGS WHERE chat_id = {chat_id};")
    print(c.fetchall())
    for index, col in enumerate(columns):
        c.execute(f"SELECT {col} FROM CHAT_SETTINGS WHERE chat_id = {chat_id};")
        temp = c.fetchone()
        if temp[0] == 0:
            settings.append("❌")
        else:
            settings.append("✅")

        print(settings)

    show_settings(update, context)
    return UPDATED


def namer(update, context):
    name = update.effective_chat.title
    if name is None:
        name = update.effective_chat.first_name
    return name


def setting_msg(setting, swap=False, set_to_swap=None):
    global msg
    if swap:
        if setting[set_to_swap] == "✅":
            setting[set_to_swap] = "❌"
        else:
            setting[set_to_swap] = "✅"

    set1, set2, set3 = setting
    msg = "How would you like me to behave?" \
          f"\nMedia reactions: {set1}️" \
          f"\nProfanity reactions: {set2}️" \
          f"\nMorning quotes: {set3}️ "
    return msg


def changed_setting(update, context):  # UPDATED

    print(update.callback_query.data)
    new_msg = setting_msg(settings, swap=True, set_to_swap=int(update.callback_query.data))
    print(new_msg)

    update.callback_query.edit_message_text(text=new_msg, reply_markup=setting_markup)
    context.bot.answer_callback_query(callback_query_id=update.callback_query.id)
    return UPDATED


def show_settings(update, context):
    if update.callback_query is None:
        chat_id = update.effective_chat.id
        context.bot.send_message(chat_id=chat_id, text=setting_msg(settings), reply_markup=setting_markup)


def cancel(update, context):
    global settings
    update.callback_query.edit_message_text(text="Settings successfully updated.")
    print("exiting")
    print(settings)
    chat_id = update.effective_chat.id
    for index, setting in enumerate(settings):
        if setting == "✅":
            settings[index] = True
        else:
            settings[index] = False
        print()
        print(settings)
        c.execute(f"UPDATE CHAT_SETTINGS SET {columns[index]}={settings[index]} WHERE CHAT_ID={chat_id};")
        conn.commit()
    c.execute(f"SELECT * FROM CHAT_SETTINGS WHERE CHAT_ID={chat_id};")
    print(c.fetchone())
    c.execute(f"SELECT CHAT_NAME FROM CHAT_SETTINGS WHERE CHAT_ID={chat_id};")
    result = c.fetchone()
    name = namer(update, context)
    print(name)
    print(result)
    print(result[0])
    if name != result[0]:
        c.execute(f"UPDATE CHAT_SETTINGS SET CHAT_NAME='{name}' WHERE CHAT_ID={chat_id};")
        conn.commit()
    settings = []
    conn.close()
    return -1
