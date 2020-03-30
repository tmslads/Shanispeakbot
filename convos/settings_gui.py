import random as r
import sqlite3

from telegram import (InlineKeyboardMarkup, InlineKeyboardButton)
from telegram.error import BadRequest

from constants import samir, harshil, sql_table

CURRENT_SETTINGS, UPDATED, PROBABILITY = range(3)

msg = None
_type = ""
morn_setting = ""
profane_prob = 0.2
media_prob = 0.3

buttons = [[InlineKeyboardButton(text="Media reactions 🎛️", callback_data="MEDIA_PROB")],
           [InlineKeyboardButton(text="Profanity reactions 🎛️", callback_data="PROFANE_PROB")],
           [InlineKeyboardButton(text="Morning quote 💬", callback_data="Morning")],
           [InlineKeyboardButton(text="Save changes 💾", callback_data="SAVE")]]

setting_markup = InlineKeyboardMarkup(buttons)

prob_buttons = [[InlineKeyboardButton(text="🔙 Back", callback_data="Back")],
                [InlineKeyboardButton(text="🔻10%", callback_data=str(-0.1)),
                 InlineKeyboardButton(text="🔻5%", callback_data=str(-0.05)),
                 InlineKeyboardButton(text="🔺5%", callback_data=str(0.05)),
                 InlineKeyboardButton(text="🔺10%", callback_data=str(0.1))],
                [InlineKeyboardButton(text="⬇0%⬇", callback_data=str(0.0)),
                 InlineKeyboardButton(text="⬆100%⬆", callback_data=str(1.0))]]

prob_markup = InlineKeyboardMarkup(prob_buttons)


def start(update, context):
    """
    Called when user uses /settings. If it is the first time using it, it creates and uses default bot settings.
    Can only be used in groups where user is admin, or in private chats.
    """
    global morn_setting, conn, c

    chat_id = update.effective_chat.id
    user_id = update.message.from_user.id

    try:
        admins = context.bot.get_chat_administrators(chat_id=chat_id)  # Get group admins
    except BadRequest:  # When it is a private chat
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

    # c.execute(f"ALTER TABLE CHAT_SETTINGS ADD MEDIA_PROB DECIMAL(2,1);")
    # c.execute(f"ALTER TABLE CHAT_SETTINGS ADD PROFANE_PROB DECIMAL(2,1);")
    # c.execute("PRAGMA table_info(CHAT_SETTINGS);")
    # c.execute(f"ALTER TABLE CHAT_SETTINGS rename TO CHAT_SETTINGS_OLD;")
    # c.execute("UPDATE CHAT_SETTINGS SET MEDIA_PROB=0.3, PROFANE_PROB=0.2 WHERE MEDIA_PROB IS NULL;")
    # c.execute("SELECT * FROM CHAT_SETTINGS;")
    # print(c.fetchall())
    # conn.commit()
    # print(result[0])
    c.execute(f"SELECT EXISTS(SELECT * FROM CHAT_SETTINGS WHERE chat_id = {chat_id});")  # Returns 0 if doesn't exist
    result = c.fetchone()

    if not result[0]:
        c.execute(f"INSERT INTO CHAT_SETTINGS VALUES({chat_id},'{name}',False,0.3,0.2);")  # First time use
        conn.commit()

    c.execute(f"SELECT MORNING_MSGS FROM CHAT_SETTINGS WHERE chat_id = {chat_id};")
    temp = c.fetchone()
    if temp[0] == 0:
        morn_setting = "❌"
    else:
        morn_setting = "✅"

    # Sends the current settings applied-
    if update.callback_query is None:
        context.bot.send_message(chat_id=chat_id, text=setting_msg(update),
                                 reply_markup=setting_markup, parse_mode="MarkdownV2")

    return UPDATED


def namer(update, context) -> str:
    """Helper function to get name of private/group chat."""

    name = update.effective_chat.title
    if name is None:
        name = update.effective_chat.first_name
    return name


def setting_msg(update, swap: bool = False):
    """Helper function to modify or create the /settings menu message."""

    global msg, media_prob, profane_prob, morn_setting
    chat_id = update.effective_chat.id
    results = []

    if swap:  # Swaps setting when user clicks button.
        if morn_setting == "✅":
            morn_setting = "❌"
        else:
            morn_setting = "✅"

    for col in ("MEDIA_PROB", "PROFANE_PROB"):
        c.execute(f"SELECT {col} FROM CHAT_SETTINGS WHERE CHAT_ID={chat_id};")
        result = c.fetchone()
        results.append(result[0])  # Append probability
        results.append(f"{int(round(result[0] * 100))}%")  # Append corresponding percent

    media_prob, media_pct, profane_prob, profane_pct = results[0], results[1], results[2], results[3]

    msg = "See is this the expected behaviour?\n\n" \
          r"1\. _Media reactions:_ " + f"{media_pct}\n" \
          r"2\. _Profanity reactions:_ " + f"{profane_pct}\n" \
          r"3\. _Morning quotes:_ " + f"{morn_setting}\n"
    return msg


def prob_message(update, kind: str, column: str) -> [None, str]:
    """Helper function to show current probability of corresponding setting."""

    chat_id = update.effective_chat.id

    if column == "":
        return

    c.execute(f"SELECT {column} FROM CHAT_SETTINGS WHERE CHAT_ID={chat_id};")
    result = c.fetchone()
    print(result[0])
    chance = f"{int(round(result[0] * 100))}%"  # Rounding it as there could be floating point round off errors.
    print(chance)

    # TODO: Shanify this
    prob_msg = f"The probability of the bot reacting to {kind} is: {chance}"
    print(prob_msg)
    return prob_msg


def prob_updater(update, context):  # PROBABILITY
    """Updates probability when buttons are pressed. Also instantly saves those values in the database."""
    global media_prob, profane_prob

    prob_diff = float(update.callback_query.data)
    chat_id = update.effective_chat.id
    call_id = update.callback_query.id
    invalid = False

    # Assign probability to common variable for simplicity-
    if _type == "media":
        _prob = media_prob
    else:
        _prob = profane_prob

    new = _prob + prob_diff  # Calculate new probability

    if prob_diff in (0.0, 1.0):  # When user clicks 0% or 100%
        new = prob_diff

    elif not 0.0 <= new <= 1.0:
        invalid = True

    col = ''
    if not invalid:  # Update database only if entry is valid.
        if _type == "media":
            media_prob = new  # Set updated value back to original variable for next callback query
            col = "MEDIA_PROB"
        else:
            profane_prob = new
            col = "PROFANE_PROB"

        c.execute(f"UPDATE CHAT_SETTINGS SET {col}={new} WHERE CHAT_ID={chat_id};")
        conn.commit()

    edit_msg = prob_message(update, kind=_type, column=col)

    if edit_msg is not None:
        try:
            update.callback_query.edit_message_text(text=edit_msg, reply_markup=prob_markup)
        except BadRequest:  # When user clicks 100% or 0% button again and again.
            pass
        context.bot.answer_callback_query(callback_query_id=call_id)

    else:  # When message is not edited, i.e. when user is stupid
        context.bot.answer_callback_query(callback_query_id=call_id,
                                          text="Are you confused? Probability is between 0% and 100% okay?",
                                          show_alert=True)

    return PROBABILITY


def change_prob(update, context):  # UPDATED
    """
    This is run when the user clicks button to change the probability. It is common for both profanity and media
    reactions.
    """

    global _type, media_prob, profane_prob

    data = update.callback_query.data
    chat_id = update.effective_chat.id
    print(data)

    if data == "MEDIA_PROB":
        _type = "media"
    else:
        _type = "profanity"

    update.callback_query.edit_message_text(text=prob_message(update, kind=_type, column=data),
                                            reply_markup=prob_markup)

    return PROBABILITY


def morn_swap(update, context):  # UPDATED
    """Used to swap states of morning quotes."""

    global morn_setting

    update.callback_query.edit_message_text(text=setting_msg(update, swap=True), reply_markup=setting_markup,
                                            parse_mode="MarkdownV2")
    context.bot.answer_callback_query(callback_query_id=update.callback_query.id)  # Clears `loading` in clients.

    return UPDATED


def go_back(update, context):  # PROBABILITY
    """Goes back to main menu."""

    update.callback_query.edit_message_text(text=setting_msg(update), reply_markup=setting_markup,
                                            parse_mode="MarkdownV2")

    return UPDATED


def save(update, context):  # UPDATED
    """Called when user clicks save. Saves all applied settings into database."""

    global morn_setting

    chat_id = update.effective_chat.id

    responses = ["I updated my behaviour", "See I got the clarity now", r"I will now like you do fo\.\.follow this",
                 "Ok I will do this now it's not that hard"]

    # TODO: Also shanify this
    update.callback_query.edit_message_text(
        text=r.choice(responses) + "\n\nMy new behaviour is:\n" + msg[36:],
        parse_mode="MarkdownV2")  # Show settings have been updated.

    # TODO: Maybe change datatype of morning_msgs to string so we don't have to do this
    # Convert the ticks and crosses into boolean form for db
    if morn_setting == "✅":
        morn_setting = True
    else:
        morn_setting = False

    c.execute(f"UPDATE CHAT_SETTINGS SET MORNING_MSGS={morn_setting} WHERE CHAT_ID={chat_id};")
    conn.commit()

    # Checks if group name has changed, if it did, updates in db-
    c.execute(f"SELECT CHAT_NAME FROM CHAT_SETTINGS WHERE CHAT_ID={chat_id};")  # Gets name from db
    result = c.fetchone()
    name = namer(update, context)  # Gets name of chat

    if name != result[0]:  # If the name is not the same, update it in db
        c.execute(f"UPDATE CHAT_SETTINGS SET CHAT_NAME='{name}' WHERE CHAT_ID={chat_id};")
        conn.commit()

    conn.close()  # Close connection, we don't want mem leaks
    return -1
