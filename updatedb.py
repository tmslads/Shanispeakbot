import os
import sqlite3

from chatbot import get_tags

os.chdir(r"C:\Users\Uncle Sam\Desktop\sthyaVERAT\4 FUN ya Practice\Shani-Sir-Telegram-Bot")
connection = sqlite3.connect('dbtest.sqlite3')
c = connection.cursor()

c.execute("SELECT id FROM statement;")
results = c.fetchall()

ids = [result[0] for result in results]

for ID in ids:
    c.execute("SELECT * FROM statement WHERE id = ?", (ID,))
    # record format: (id, text, search_text, conversation, created_at, in_response_to, search_in_response_to, persona)
    record = c.fetchall()[0]

    text = record[1]
    in_response_to = record[5]

    search_text = get_tags(text)
    if in_response_to is not None:
        search_in_response_to = get_tags(in_response_to)
    else:
        search_in_response_to = "NULL"
    print(search_text, search_in_response_to)
    c.execute("UPDATE statement SET search_text = ? WHERE id = ?", (search_text, ID))
    c.execute("UPDATE statement SET search_in_response_to = ? WHERE id = ?", (search_in_response_to, ID))

connection.commit()
print('Completed.')
