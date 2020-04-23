from datetime import datetime

from telegram.ext import CallbackContext

from helpers.db_connector import connection
from helpers.logger import logger


def morning_goodness(context: CallbackContext) -> None:
    """
    Send a "good morning" quote to the groups, along with a clip. This will only work if it has already been a
    day since last good morning quote and is before 11am the next day.
    """

    right_now = datetime.now()  # returns: Datetime obj
    afternoon = datetime(right_now.year, right_now.month, right_now.day, 11)  # 11am today

    if 'last_sent' not in context.bot_data:
        context.bot_data['last_sent'] = right_now

    diff = right_now - context.bot_data['last_sent']

    # Send only if it has been over a day and is before 11am next morning since last good morning message-
    if diff.days < 1 and right_now >= afternoon:
        return

    with open("files/good_mourning.txt", "r") as greetings:
        position = context.bot_data['seek']
        if position == 13642:  # If EOF was reached
            position = 0  # Start from the beginning
        greetings.seek(position)

        greeting = greetings.readline()
        logger(message=f"Today's morning quote is:\n{greeting}")
        context.bot_data['seek'] = greetings.tell()

    query = "SELECT CHAT_ID, CHAT_NAME FROM CHAT_SETTINGS WHERE MORNING_MSGS='✅';"
    ids = connection(query, fetchall=True)
    logger(message=f"The query executed on the database was:\n{query}\nand the result was:\n{ids=}")

    # Open mp3 from desktop as github url doesn't support thumbnails-

    clip_loc = r"C:/Users/Uncle Sam/Desktop/sthyaVERAT/4 FUN ya Practice/Shanisirmodule/Assets/clips/good mourning.mp3"

    for chat in ids:

        chat_id = chat[0]
        chat_name = chat[1]

        try:
            msg = context.bot.send_message(chat_id=chat_id, text=greeting)
            logger(message=f"Today's morning quote was just sent to {chat_name}.")

            context.bot.send_chat_action(chat_id=chat_id, action='upload_audio')

            context.bot.send_audio(chat_id=chat_id, title="Good morning", performer="Shani sir",
                                   audio=open(clip_loc, "rb"), thumb=open("files/shanisir.jpeg", 'rb'))
            logger(message=f"Today's morning audio was just sent to {chat_name}.")

            context.bot.pin_chat_message(chat_id=chat_id, message_id=msg.message_id, disable_notification=True)

        except Exception as e:  # When chat is private, no rights to pin message, or if bot was removed.
            logger(message=f"There was an error for {chat_name} due to: {e}.")

    context.bot_data['last_sent'] = datetime(right_now.year, right_now.month, right_now.day, 8)  # Set it as 8AM today
    context.dispatcher.persistence.update_bot_data(context.bot_data)
    logger(message="The last_sent object was successfully updated to 8AM today.")
