# Helper function to connect to database and get result.
import sqlite3
from typing import Union

from telegram import Update

from helpers.namer import get_chat_name


def connection(query: str, update: Update = None, fetchall: bool = False) -> Union[list, int, float, str]:
    """Connect to database and execute given query."""

    conn = sqlite3.connect('./files/bot_settings.db')
    c = conn.cursor()

    if update is not None:
        chat_id = update.effective_chat.id
        c.execute(f"SELECT EXISTS(SELECT * FROM CHAT_SETTINGS WHERE chat_id = {chat_id});")
        result = c.fetchone()

        if not result[0]:  # If /settings was never called
            name = get_chat_name(update)

            c.execute(f"INSERT INTO CHAT_SETTINGS VALUES({chat_id},'{name}','❌',0.3,0.2);")  # First time use
            conn.commit()

    c.execute(query)

    if fetchall:
        result = c.fetchall()
    else:
        result = c.fetchone()
        result = result[0]

    conn.close()

    return result
