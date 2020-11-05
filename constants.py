# Group IDs-
group_ids = {'12b': '-1001396726510', 'grade12': '-1001210862980', 'wait': '-1001427310423',
             'testing': '-1001248269460', 'pass': '-375666484'}

# IDs of 12B members-
class_12b = (['Adeep', 1020219808], ['Angelia', 1022262231], ['Ann', 1066540678], ['Areeb', 894016631],
['Ashwin', 945493887], ['Uma', 849013424], ['Harshil', 476269395], ['Jaden', 847874359],
['Joel', 956373228], ['Juanita', 1051874191], ['Nikil', 862351464], ['Raghu', 901026387],
['Rithima', 1056304399], ['Ronit', 869309961], ['Sahel', 1162928454], ['Sakshi', 995415013],
['Samir', 764886971], ['Samrin', 1009248402], ['Satya', 897385101], ['Shweda', 1061449075],
['Suhail', 661121682])

# The bot makers-
samir = 764886971
harshil = 476269395

# The bot itself-
bot_id = 997899425

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
