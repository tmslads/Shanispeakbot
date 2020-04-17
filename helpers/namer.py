# Functions to obtain nickname or chatname-
from telegram import Update
from telegram.ext import CallbackContext


def get_nick(update: Update, context: CallbackContext) -> str:
    """Uses current nickname set by user."""

    try:
        name = context.user_data['nickname'][-1]
    except (KeyError, IndexError):
        context.user_data['nickname'] = [update.message.from_user.first_name]
    finally:
        return context.user_data['nickname'][-1]


def get_chat_name(update: Update) -> str:
    """Helper function to get name of private/group chat."""

    name = update.effective_chat.title
    if name is None:
        name = update.effective_chat.first_name
    return name
