import random
from datetime import datetime

from telegram.ext import CallbackContext

from helpers.db_connector import connection
from helpers.logger import logger


def morning_goodness(context: CallbackContext) -> None:
    """
    Send a "good morning" quote to the groups, along with a clip. This will only work if it has already been a
    day since last good morning quote and is between 8 and 11am the next day.
    """

    right_now = datetime.now()  # returns: Datetime obj
    afternoon = datetime(right_now.year, right_now.month, right_now.day, 11)  # 11am today
    eight_am = datetime(right_now.year, right_now.month, right_now.day, 8)

    if 'last_sent' not in context.bot_data:
        context.bot_data['last_sent'] = right_now

    context.bot_data.setdefault('pin_msgs', [])

    diff = right_now - context.bot_data['last_sent']

    # Send only if it has been over a day since last good morning message and current time is between 8 and 11AM-
    if diff.days < 1 or right_now >= afternoon or right_now <= eight_am:
        return

    with open("files/good_mourning.txt", "r+") as greetings:
        quotes = greetings.readlines()
        position = context.bot_data['seek']
        if position == 13642:  # if EOF was reached
            position = 0  # start from the beginning
            random.shuffle(quotes)  # randomise order of quotes
            greetings.writelines(quotes)
        greetings.seek(position)

        greeting = greetings.readline()
        logger(message=f"Today's morning quote is:\n{greeting}")
        context.bot_data['seek'] = greetings.tell()  # update file cursor position

    query = "SELECT CHAT_ID, CHAT_NAME FROM CHAT_SETTINGS WHERE MORNING_MSGS='✅';"
    ids = connection(query, fetchall=True)
    logger(message=f"The query executed on the database was:\n{query}\nand the result was:\n{ids=}")

    # Open mp3 from desktop as github url doesn't support thumbnails-
    clip_loc = r"C:/Users/Uncle Sam/Desktop/sthyaVERAT/4 FUN ya Practice/Shanisirmodule/Assets/clips/bell.mp3"

    for chat_id, chat_name in ids:
        try:
            msg = context.bot.send_message(chat_id=chat_id, text=greeting)
            logger(message=f"Today's morning quote was just sent to {chat_name}.")

            context.bot.send_chat_action(chat_id=chat_id, action='upload_audio')

            context.bot.send_audio(chat_id=chat_id, title="Good morning", performer="Shani sir",
                                   audio=open(clip_loc, "rb"), thumb=open("files/shanisir.jpeg", 'rb'))
            logger(message=f"Today's morning audio was just sent to {chat_name}.")

            context.bot.pin_chat_message(chat_id=chat_id, message_id=msg.message_id, disable_notification=True)

            context.bot_data['pin_msgs'].append(msg)

        except Exception as e:  # Insufficient permissions, bot removal/block, or any other unexpected error
            logger(message=f"There was an error for {chat_name} due to: {e}.")

    context.bot_data['last_sent'] = eight_am  # Set it as 8AM today
    context.dispatcher.persistence.update_bot_data(context.bot_data)
    logger(message="The last_sent object was successfully updated to 8AM today.")

    del right_now, afternoon, eight_am, diff, greeting, query, ids, clip_loc
