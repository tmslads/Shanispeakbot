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
                                      " Or just talk to me here and get help from me directly. Type /help to know more")

    @staticmethod
    def helper(update, context):
        context.bot.send_message(chat_id=update.effective_chat.id,
                                 text="This bot sends you actual shani sir clips straight from Shanisirmodule! "
                                      "He is savage in groups too!"
                                      "\n\nHow to get clips (Inline mode):"
                                      "\n@ me in the chatbox (don't press send yet!), press space and then type"
                                      " to get a clip."
                                      "\n\nCommands available:"
                                      "\n/help - This will literally print this message again."
                                      "\n/start - Starts the bot in private chat."
                                      "\n/swear - Teaches you not to swear."
                                      "\n/snake - A roast."
                                      "\n/facts - A totally useful fact."
                                      "\n/8ball - Gives an answer to yes/no questions in Shani Sir style!"
                                      "\nUsage:\n1. Reply to a message with /8ball\n2. Send /8ball in chat, and reply to the message the bot sends."
                                      " Inspired by the Shani Sir Module and Telegram."
                                 )

    @staticmethod
    def secret(update, context):
        context.bot.send_message(chat_id=update.effective_chat.id,
                                 text="stop finding secret commands :P")  # Secret command for later use

    @staticmethod
    def swear(update, context):
        BotCommands.delete_command(update)
        while True:
            swears = r.choices(prohibited, k=4)  # Returns a list of 4 elements
            if len(set(swears)) == len(swears):  # i.e. if there is a duplicate element
                break
        context.bot.send_message(chat_id=update.effective_chat.id,
                                 text=f"'{swears[0]}',\n'{swears[1]}',\n'{swears[2]}',\n'{swears[3]}'\n\n"
                                      f"{next(swear_advice)}".swapcase())

    @staticmethod
    def snake(update, context):
        BotCommands.delete_command(update)
        context.bot.send_message(chat_id=update.effective_chat.id,
                                 text=snake_roast)

    @staticmethod
    def facts(update, context):
        BotCommands.delete_command(update)
        fact = r.choice(util.facts())
        context.bot.send_message(chat_id=update.effective_chat.id,
                                 text=fact)

    @staticmethod
    def unknown(update, context):
        context.bot.send_message(chat_id=update.effective_chat.id, text="I didn't say wrong I don't know.")
