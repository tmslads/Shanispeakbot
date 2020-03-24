import sqlite3

from telegram.ext import BaseFilter
from constants import sql_table


def connection(update, query):
    """Connect to database and execute given query."""

    conn = sqlite3.connect('./files/bot_settings.db')
    c = conn.cursor()
    chat_id = update.effective_chat.id

    try:
        c.execute(query)
        c.execute(f"SELECT EXISTS(SELECT * FROM CHAT_SETTINGS WHERE chat_id = {chat_id});")
        result = c.fetchone()
        if not result[0]:
            raise Exception
    except Exception as e:  # If /settings was never called
        print(e)
        name = update.effective_chat.title
        if name is None:
            name = update.effective_chat.first_name

        c.execute(sql_table)
        c.execute(f"INSERT INTO CHAT_SETTINGS VALUES({chat_id},'{name}',True,True,False);")
        conn.commit()
    finally:
        c.execute(query)

    result = c.fetchone()
    conn.close()

    return result[0]

# See docs for how these work-


class MediaReactions(BaseFilter):
    update_filter = True
    name = "CustomFilters.settings.media_settings"

    def filter(self, update):
        result = connection(update,
                            f"SELECT media_reactions from chat_settings where CHAT_ID={update.effective_chat.id};")

        return bool(result)


reactions = MediaReactions()


class ProfanityCheck(BaseFilter):
    update_filter = True
    name = "CustomFilters.settings.profanity_settings"

    def filter(self, update):
        result = connection(update,
                            f"SELECT profanity_check from CHAT_SETTINGS where CHAT_ID={update.effective_chat.id};")

        return bool(result)


profanity = ProfanityCheck()


class MorningMsgs(BaseFilter):
    update_filter = True
    name = "CustomFilters.settings.morning_settings"

    def filter(self, update):
        result = connection(update, f"SELECT morning_msgs from CHAT_SETTINGS where CHAT_ID={update.effective_chat.id};")

        return bool(result)


morning = MorningMsgs()
