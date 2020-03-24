import sqlite3
import random as r
from telegram import (InlineKeyboardMarkup, InlineKeyboardButton)
from telegram import error

from constants import samir, harshil, sql_table

CURRENT_SETTINGS, UPDATED = range(2)

msg = None

settings = []
columns = ["media_reactions", "profanity_check", "morning_msgs"]

# callback_data is set to 0,1,2 since they correspond to index of `columns`
buttons = [[InlineKeyboardButton(text="Media reactions", callback_data=str(0))],
           [InlineKeyboardButton(text="Profanity checker", callback_data=str(1))],
           [InlineKeyboardButton(text="Morning quote", callback_data=str(2))],
           [InlineKeyboardButton(text="Save changes", callback_data="SAVE")]]
setting_markup = InlineKeyboardMarkup(buttons)


def start(update, context):
    """
    Called when user uses /settings. If it is the first time using it, it creates and uses default bot settings.
    Can only be used in groups where user is admin, or in private chats.
    """
    global settings, conn, c

    chat_id = update.effective_chat.id
    user_id = update.message.from_user.id

    try:
        admins = context.bot.get_chat_administrators(chat_id=chat_id)  # Get group admins
    except error.BadRequest:  # When it is a private chat
        pass
    else:
        for admin in admins:
            if user_id in (samir, harshil) or admin.user.id == user_id:  # Check if admin/creators are calling /settings
                break
        else:
            responses = ["I'm not allowing you like you say", "Ask the permission then only",
                         "This is not for you okay?", "Only few of them can do this not all okay?",
                         "See not you so sowry"]
            context.bot.send_message(chat_id=chat_id,
                                     text=r.choice(responses),
                                     reply_to_message_id=update.message.message_id)
            return -1  # Stop convo since a regular user called /settings

    conn = sqlite3.connect('./files/bot_settings.db')
    c = conn.cursor()
    name = namer(update, context)

    c.executescript(sql_table)  # If table is not made
    conn.commit()

    c.execute(f"SELECT EXISTS(SELECT * FROM CHAT_SETTINGS WHERE chat_id = {chat_id});")  # Returns 0 if doesn't exist
    result = c.fetchone()

    if not result[0]:
        c.execute(f"INSERT INTO CHAT_SETTINGS VALUES({chat_id},'{name}',True,True,False);")  # First time use
        conn.commit()

    # Enabled settings are converted to ticks, disabled to cross marks-
    for index, col in enumerate(columns):
        c.execute(f"SELECT {col} FROM CHAT_SETTINGS WHERE chat_id = {chat_id};")
        temp = c.fetchone()
        if temp[0] == 0:
            settings.append("❌")
        else:
            settings.append("✅")

    # Sends the current settings applied-
    if update.callback_query is None:
        context.bot.send_message(chat_id=chat_id, text=setting_msg(settings), reply_markup=setting_markup)

    return UPDATED


def namer(update, context):
    """Gets name of private/group chat and returns it."""

    name = update.effective_chat.title
    if name is None:
        name = update.effective_chat.first_name
    return name


def setting_msg(setting: list, swap: bool = False, set_to_swap=None):
    """Modifies or creates the settings menu message and returns it."""

    global msg
    if swap:  # Swaps setting when user clicks button.
        if setting[set_to_swap] == "✅":
            setting[set_to_swap] = "❌"
        else:
            setting[set_to_swap] = "✅"

    set1, set2, set3 = setting  # Since settings will always have 3 elements
    msg = "See is this the expected behaviour?" \
          f"\nMedia reactions: {set1}️" \
          f"\nProfanity reactions: {set2}️" \
          f"\nMorning quotes: {set3}️ "
    return msg


def changed_setting(update, context):  # UPDATED
    """When user clicks button to change setting."""

    new_msg = setting_msg(settings, swap=True, set_to_swap=int(update.callback_query.data))

    update.callback_query.edit_message_text(text=new_msg, reply_markup=setting_markup)  # Edit message to show change
    context.bot.answer_callback_query(callback_query_id=update.callback_query.id)  # Clears `loading` in clients.

    return UPDATED


def cancel(update, context):
    """Called when user clicks save. Saves all applied settings into database."""

    global settings
    responses = ["I updated my behaviour", "See I got the clarity now", "I will now like you do fo..follow this",
                 "Ok I will do this now it's not that hard"]
    update.callback_query.edit_message_text(text=r.choice(responses))  # Show settings have been updated.
    chat_id = update.effective_chat.id

    # Convert the ticks and crosses into boolean form for db
    for index, setting in enumerate(settings):
        if setting == "✅":
            settings[index] = True
        else:
            settings[index] = False

        c.execute(f"UPDATE CHAT_SETTINGS SET {columns[index]}={settings[index]} WHERE CHAT_ID={chat_id};")
        conn.commit()

    # Checks if group name has changed, if it did, updates in db.
    c.execute(f"SELECT CHAT_NAME FROM CHAT_SETTINGS WHERE CHAT_ID={chat_id};")
    result = c.fetchone()
    name = namer(update, context)

    if name != result[0]:
        c.execute(f"UPDATE CHAT_SETTINGS SET CHAT_NAME='{name}' WHERE CHAT_ID={chat_id};")
        conn.commit()

    settings.clear()  # Clear settings list so next run will be fresh.
    conn.close()  # Close connection, we don't want mem leaks
    return -1
