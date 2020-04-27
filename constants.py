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
                MORNING_MSGS TEXT,
                MEDIA_PROB DECIMAL(2,1),
                PROFANE_PROB DECIMAL(2,1)
            );
            """

# Websites to scrape from-
LINK = "https://api.github.com/repos/tmslads/shanisirmodule/contents/Assets/clips"
FACT_URL = 'http://randomfactgenerator.net/'  # To be scraped for facts()
QUIZ_URL = "https://www.onlinegk.com/general-knowledge/gk-question-answers/physics"

# Bot usernames-
shanibot = "@shanisirbot"
testbot = "@Ttessttingbot"
