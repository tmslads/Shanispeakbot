# Group ids-

group_ids = {'12b': '-1001396726510', 'grade12': '-1001210862980', 'wait': '-1001427310423',
             'testing': '-1001248269460', 'pass': '-375666484'}

# The bot makers-
samir = 764886971
harshil = 476269395

# Table-
sql_table = """
            CREATE TABLE IF NOT EXISTS CHAT_SETTINGS(
                CHAT_ID INTEGER PRIMARY KEY,
                CHAT_NAME TEXT,
                MEDIA_REACTIONS BOOLEAN,
                PROFANITY_CHECK BOOLEAN,
                MORNING_MSGS BOOLEAN
            );
            """
# Websites to scrape from-

_DOWNLOAD = "https://raw.githubusercontent.com"
_LINK = "https://github.com/tmslads/Shanisirmodule/tree/haunya/Assets/clips"
URL = 'http://randomfactgenerator.net/'  # To be scraped for facts()
