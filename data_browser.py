import pickle
import sqlite3
import pprint

connection = sqlite3.connect('db.sqlite3')
c = connection.cursor()

file = open('./files/user_data', 'rb')
data = pickle.load(file)  # In the form of a dictionary
user_data = data['user_data']  # A dictionary within the data dict


def pprint_view() -> None:
    """Pretty print the entire data dictionary"""
    pprint.PrettyPrinter(indent=2).pprint(data)


def print_ids() -> None:
    """Print user IDs of all known users of bot"""
    for user in user_data:
        print(user)


def get_data(user: int) -> None:
    """Print data of given user"""
    print(f"User ID: {user}\n"
            f"Full name: {user_data[user]['full_name']}\n"
            f"Nickname: {user_data[user]['nickname']}\n"
            f"Birthday: {user_data[user]['birthday']}\n"
            "Quiz info-\n"
            f"Total questions answered: {data['bot_data']['quizizz'][user]['questions_answered']}\n"
            f"Total correct answers: {data['bot_data']['quizizz'][user]['answers_right']}\n")