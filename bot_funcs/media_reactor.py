import random as r
from time import sleep, time as cur_time

from telegram import Update
from telegram.ext import CallbackContext

from helpers.db_connector import connection
from helpers.logger import logger
from helpers.namer import get_nick

last_reacted_at = 0


def media(update: Update, context: CallbackContext) -> None:
    """Sends a reaction to media messages (pictures, videos, documents, voice notes)"""

    global last_reacted_at

    if cur_time() - last_reacted_at < 60:  # If a reaction was sent less than a minute ago
        return  # Don't send a reaction

    last_reacted_at = cur_time()

    chat_id = update.effective_chat.id
    msg = update.message.message_id
    name = get_nick(update, context)
    query = f"SELECT MEDIA_PROB FROM CHAT_SETTINGS WHERE CHAT_ID={chat_id};"

    true = connection(query, update)
    logger(message=f"The query executed on the database was:\n{query}\nand the result was:\n{true=}")

    false = 1 - true

    prob = r.choices([0, 1], weights=[false, true])[0]  # Probabilities are 0.7 - False, 0.3 - True by default

    if not prob:
        return

    if hasattr(update.message.audio, 'performer'):
        if update.message.audio.performer == 'Shani Sir':  # Don't send reaction to its own inline clips.
            return

    try:
        doc = update.message.document.file_name.split('.')[-1]
    except Exception as e:  # When there is no document sent (most likely AttributeError)
        logger(message=f"File extension was not assigned. The warning is: \n{e}", warning=True)
        doc = ''

    img_reactions = ("😂", "🤣", "😐", f"Not funny {name} okay?", "This is not fine like you say", "*giggles*",
                     f"This is embarrassing to me {name}", "What your doing?! Go for the worksheet",
                     "I don't like this now", "This is beneficial to me like", f"I don't understand this {name}",
                     f"See {name}, I want you to delete this")

    vid_reactions = ("😂", "🤣", "😐", f"I've never seen anything like this {name}", "What is this",
                     f"Tell me the physics behind it {name}", "This is like you say boring", "Now I feel very bad like",
                     f"Are you fine {name}?", f"See {name}, I want you to delete this")

    voice_reactions = ("What is this", f"I can't hear you {name}", f"Are you fine {name}?",
                       "Now your on the track like", "Your voice is funny like you say",
                       f"See I can't tolerate this {name}", "What your saying??",
                       f"See {name}, I want you to delete this")

    app_reactions = ("Is this a virus", "I'm just suggesting like, don't open this", "We just don't mind that okay?")

    doc_reactions = (f"Did you read this {name}", "I'm not in agreement like", "I don't like this okay",
                     "This is very good like you say", "Now your on the track like", "Nice for reading okay",
                     "This is fake news delete this like", "This is like you say cut and paste from somewhere")

    context.bot.send_chat_action(chat_id=chat_id, action='typing')
    sleep(2)

    if update.message.photo or doc in ('jpg', 'jpeg', 'png'):
        context.bot.send_message(chat_id=chat_id, text=r.choice(img_reactions), reply_to_message_id=msg)
        logger(message=f"Bot sent a reaction to a photo to {name}.")

    elif update.message.voice or update.message.audio:
        context.bot.send_message(chat_id=chat_id, text=r.choice(voice_reactions), reply_to_message_id=msg)
        logger(message=f"Bot sent a reaction to a voice message/audio to {name}.")

    elif update.message.video or doc in ('mp4', 'gif'):
        context.bot.send_message(chat_id=chat_id, text=r.choice(vid_reactions), reply_to_message_id=msg)
        logger(message=f"Bot sent a reaction to a video to {name}.")

    elif doc in ('apk', 'exe'):
        context.bot.send_message(chat_id=chat_id, text=r.choice(app_reactions), reply_to_message_id=msg)
        logger(message=f"Bot sent a reaction to a executable to {name}.")

    elif doc in ('pdf', 'doc', 'docx', 'txt'):
        context.bot.send_message(chat_id=chat_id, text=r.choice(doc_reactions), reply_to_message_id=msg)
        logger(message=f"Bot sent a reaction to a text document to {name}.")

    else:
        logger(message=f"This shouldn't be happening, bot needs to respond to at least one of the media."
                       f"The file extension was {doc=}.", warning=True)

    del chat_id, name, msg, query, true, false, prob, app_reactions, img_reactions, vid_reactions, voice_reactions, \
        doc_reactions
