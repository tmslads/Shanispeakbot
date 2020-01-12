import itertools
import random as r

import util

with open(r"text_files/lad_words.txt", "r") as f:
    prohibited = f.read().lower().split('\n')

with open(r"text_files/snake.txt", "r") as f:
    snake_roast = f.read()

swear_advice = ["Don't use such words. Okay, fine?", "Such language fails to hit the tarjit.",
                "Vocabulary like this really presses my jokey.", "It's embarrassing vocabulary like basically.",
                "Such language is not expected from 12th class students",
                "You say shit like this then you go 'oh i'm so sowry sir it slipped' and expect me to forgive your"
                " sorry ass. Pathetic. Get a grip, loser.",
                "Some of you dumbasses talk as if your teachers are all deaf. Trust me; we hear a lot more than you'd"
                " like us to.", "There's no meaning of soo sowry, okay?"]
r.shuffle(swear_advice)
swear_advice = itertools.cycle(swear_advice)


class BotCommands:
    @staticmethod
    def delete_command(update):
        """Delete the command message sent by the user"""
        update.message.delete()

    @staticmethod
    def start(update, context):
        context.bot.send_message(chat_id=update.effective_chat.id,
                                 text="You can use me anywhere, @ me in the chatbox and type to get an audio clip."
                                      " Or just talk to me here and get help from me directly.")

    @staticmethod
    def helper(update, context):
        context.bot.send_message(chat_id=update.effective_chat.id,
                                 text="This bot sends you actual shani sir clips straight from Shanisirmodule! "
                                      "He is savage in groups too!"
                                      " @ me in the chatbox (don't press enter yet!), press space and then type"
                                      " to get a clip. and type to get an audio clip."
                                      " P.S: Download Shanisirmodule from:"
                                      " https://github.com/tmslads/Shanisirmodule/releases")

    @staticmethod
    def secret(update, context):
        context.bot.send_message(chat_id=update.effective_chat.id, text="stop finding secret commands :P")

    @staticmethod
    def swear(update, context):
        BotCommands.delete_command(update)
        while True:
            swears = r.choices(prohibited, k=4)  # Returns a list of 4 elements
            if len(set(swears)) == len(swears):  # i.e. if there is a duplicate element
                break
        context.bot.send_message(chat_id=update.effective_chat.id,
                                 text=f"'{swears[0]}',\n'{swears[1]}',\n'{swears[2]}',\n'{swears[3]}'\n\n"
                                      f"{next(swear_advice)}")

    @staticmethod
    def snake(update, context):
        BotCommands.delete_command(update)
        context.bot.send_message(chat_id=update.effective_chat.id,
                                 text=snake_roast)

    @staticmethod
    def facts(update, context):
        BotCommands.delete_command(update)
        factoid = util.facts()
        facts = [factoid[0].getText()[:-6], factoid[1].getText()[:-6],
                 factoid[2].getText()[:-6]]  # List of three random facts
        context.bot.send_message(chat_id=update.effective_chat.id,
                                 text=r.choice(facts))

    @staticmethod
    def unknown(update, context):
        context.bot.send_message(chat_id=update.effective_chat.id, text="I didn't say wrong I don't know.")
