import pickle
import sqlite3
import pprint

connection = sqlite3.connect('db.sqlite3')
c = connection.cursor()

file = open('./files/user_data', 'rb')
data = pickle.load(file)  # In the form of a dictionary


def pprint_view():
        pprint.PrettyPrinter(indent=2).pprint(data)


pass