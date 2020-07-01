from telegram import Update
from telegram.ext import CallbackContext
from helpers.logger import logger


def welcome(update: Update, context: CallbackContext) -> None:
    """
    Greets new users in the TMS group and also sends a link to the Introducing Telegram channel where they can
    learn more about Telegram.
    """
    user = update.message.new_chat_members[0]
    logger(message=f"{user.full_name} just joined the TMS group!")

    context.bot.send_message(chat_id=update.effective_chat.id,
                             text=f'Welcome to the TMS group '
                                  f'{user.mention_html()}! I want you to know all Telegram like you say features okay? '
                                  f'Check out this '
                                  f'<a href="https://t.me/IntroducingTelegram">channel</a> to know everything!',
                             parse_mode="HTML")
