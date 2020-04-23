import logging

from telegram import Update

from .namer import get_chat_name

# asctime - The time in human readable form
# name - Name of the logger module
# levelname - logging level for the message ('DEBUG', 'INFO', 'WARNING', 'ERROR', 'CRITICAL')
# lineno - Line number
# message - The logged message

logging.basicConfig(format='%(asctime)s - %(name)s - %(levelname)s - %(lineno)d - %(message)s', level=logging.INFO)


def logger(message: str, update: Update = None, command: bool = False, warning: bool = False,
           exception: bool = False) -> None:
    if warning:
        logging.warning(f"\n{message}\n\n")
    elif exception:
        logging.exception(f"\n{message}\n\n")
    else:
        if command and update is not None:
            logging.info(f"\n{update.effective_user.first_name} just used {message} in {get_chat_name(update)}.\n\n")
        else:
            logging.info(f"\n{message}\n\n")
