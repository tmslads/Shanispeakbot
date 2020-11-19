from datetime import datetime

from telegram import Update
from telegram.ext import CallbackContext

from helpers.logger import logger


def de_pin(update: Update, context: CallbackContext) -> None:
    """Deletes pinned message service status from the bot."""

    context.bot.delete_message(chat_id=update.effective_chat.id, message_id=update.message.message_id)
    logger(message=f"Bot deleted a pinned service message from {update.effective_chat.title}.")


def unpin_all(context: CallbackContext) -> None:
    """Unpins all messages pinned by bot once daily."""

    pin_msgs = context.bot_data['pin_msgs']
    if not pin_msgs or (pin_msgs and (datetime.now() - pin_msgs[0].date).days == 0):  # del if >= 1 day has passed
        return

    for msg in pin_msgs:  # We don't use unpin_all_chat_messages as we want to unpin msgs only from this bot
        msg.unpin()

    pin_msgs.clear()
