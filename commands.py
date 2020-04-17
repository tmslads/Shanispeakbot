import itertools
import logging
import random as r

from telegram import error, InlineKeyboardButton, InlineKeyboardMarkup, Poll, Update
from telegram.ext import CallbackContext

from online import util, quiz_scraper
from helpers.namer import get_chat_name

with open(r"files/lad_words.txt", "r") as f:
    prohibited = f.read().lower().split('\n')

with open(r"files/snake.txt", "r") as f:
    snake_roast = f.read()

logging.basicConfig(format='%(asctime)s - %(module)s - %(levelname)s - %(lineno)d - %(message)s', level=logging.INFO)

swear_advice = ["Don't use such words. Okay, fine?", "Such language fails to hit the tarjit.",
                "Vocabulary like this really presses my jokey.", "It's embarrassing vocabulary like basically.",
                "Such language is not expected from 12th class students", "There's no meaning of soo sowry, okay?",
                "You say shit like this then you go 'oh i'm so sowry sir it slipped' and expect me to forgive your"
                " sorry ass. Pathetic. Get a grip, loser.",
                "Some of you dumbasses talk as if your teachers are all deaf. Trust me; we hear a lot more than you'd"
                " like us to."]

r.shuffle(swear_advice)
swear_advice = itertools.cycle(swear_advice)


def ladcased(normal: str) -> str:
    """Convert a string to 'ladcase' (Alternating uppercase and lowercase)"""

    ladified = ''
    for i, c in enumerate(normal):
        ladified += c.lower() if (i % 2 == 0) else c.upper()

    return ladified


def del_command(update: Update) -> None:
    """Delete the command message sent by the user."""

    try:
        update.message.delete()

    except error.BadRequest:
        pass


class BotCommands:
    @staticmethod
    def start(update: Update, context: CallbackContext) -> None:

        name = update.effective_user.first_name

        msg = "You can use me anywhere, @ me in the chatbox and type to get an audio clip." \
              " Or just talk to me here and get help from me directly. Type /help to know more"

        logging.info(f"\n{name} just used /start in {get_chat_name(update)}.\n\n")

        if context.args:
            args = context.args[0]  # Gather deep linked payload attached to /start
            msg = "See if you want to tell your nickname and birthday click this --> /tell"
            logging.info(f"\n{name} just clicked the button to use /tell in private from {get_chat_name(update)}.\n\n")

        context.bot.send_message(chat_id=update.effective_chat.id, text=msg)

    @staticmethod
    def helper(update: Update, context: CallbackContext) -> None:

        buttons = [[InlineKeyboardButton(text="Try out inline mode", switch_inline_query_current_chat="")],
                   [InlineKeyboardButton(text="Use inline mode in another chat", switch_inline_query="")]]
        markup = InlineKeyboardMarkup(buttons)

        context.bot.send_message(chat_id=update.effective_chat.id,
                                 text=r"This bot sends you audio clips straight from the Shani Sir Module\."
                                      "He's savage when he's cranky\."
                                      "\n\nHow to get clips \(Inline mode\):"
                                      "\n@ me in the chatbox \(don't press send yet\!\), press space and then type"
                                      r" to get a clip\."
                                      "\n\nCommands available:"
                                      "\n/help \- This will literally just send this message again\."
                                      "\n/start \- Starts the bot in private chat\."
                                      "\n/swear \- Teaches you not to swear\."
                                      "\n/snake \- Sends you a roast\."
                                      "\n/facts \- Blesses you with an incredibly useful fact\."
                                      "\n/8ball \- Answers yes/no questions in Shani Sir style\!"
                                      "\n/settings \- Modify my behaviour with granular precision\."
                                      "\n\nHow to use /8ball:\n1\. Reply to a message with /8ball\n2\. Send /8ball in"
                                      " chat and reply to the message the bot sends\.\n\n"
                                      r"Inspired by the [Shani Sir Module](https://github.com/tmslads/Shanisirmodule)"
                                      r" and Telegram\.",
                                 parse_mode="MarkdownV2", disable_web_page_preview=True, reply_markup=markup
                                 )

        logging.info(f"\n{update.effective_user.first_name} just used /help in {get_chat_name(update)}.\n\n")

    @staticmethod
    def secret(update: Update, context: CallbackContext) -> None:
        context.bot.send_message(chat_id=update.effective_chat.id,
                                 text="stop finding secret commands :P")  # Secret command for later use

    @staticmethod
    def swear(update: Update, context: CallbackContext) -> None:
        del_command(update)

        while True:
            swears = r.choices(prohibited, k=4)  # Returns a list of 4 elements
            if len(set(swears)) == len(swears):  # i.e. if there is a duplicate element
                break

        context.bot.send_message(chat_id=update.effective_chat.id,
                                 text=ladcased(f"'{swears[0]}',\n'{swears[1]}',\n'{swears[2]}',\n'{swears[3]}'\n\n"
                                               f"{next(swear_advice)}"))
        logging.info(f"\n{update.effective_user.first_name} just used /swear in {get_chat_name(update)}.\n\n")

    @staticmethod
    def snake(update: Update, context: CallbackContext) -> None:
        del_command(update)
        context.bot.send_message(chat_id=update.effective_chat.id, text=snake_roast)
        logging.info(f"\n{update.effective_user.first_name} just used /snake in {get_chat_name(update)}.\n\n")

    @staticmethod
    def facts(update: Update, context: CallbackContext) -> None:
        del_command(update)
        fact = r.choice(util.facts())
        context.bot.send_message(chat_id=update.effective_chat.id, text=fact)
        logging.info(f"\n{update.effective_user.first_name} just used /facts in {get_chat_name(update)}.\n\n")

    @staticmethod
    def quizizz(update: Update, context: CallbackContext) -> None:

        while True:
            try:
                questions, choices, answers = quiz_scraper.a_quiz()
                break
            except TypeError:  # If we get None (due to error) back, retry.
                logging.warning(f"\nThere was a problem getting the questions, trying again.\n\n")

        question = questions[0]
        options = choices[0]
        answer = answers[0]
        context.bot.send_poll(chat_id=update.effective_chat.id, question=question, options=options, is_anonymous=False,
                              type=Poll.QUIZ, correct_option_id=answer)
        logging.info(f"\n{update.effective_user.first_name} just used /quizizz in {get_chat_name(update)}.\n\n")

    @staticmethod
    def unknown(update: Update, context: CallbackContext) -> None:
        context.bot.send_message(chat_id=update.effective_chat.id, text="I didn't say wrong I don't know.")
        logging.info(f"\n{update.effective_user.first_name} just used something weird in {get_chat_name(update)}.\n\n")
