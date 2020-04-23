from telegram import Update
from telegram.ext import CallbackContext

from helpers.logger import logger


def de_pin(update: Update, context: CallbackContext) -> None:
    """Deletes pinned message service status from the bot."""

    context.bot.delete_message(chat_id=update.effective_chat.id, message_id=update.message.message_id)
    logger(message=f"Bot deleted a pinned service message from {update.effective_chat.title}.")
