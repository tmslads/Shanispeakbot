import logging
import pickle
import pprint

from telegram.ext import (CommandHandler, ConversationHandler, InlineQueryHandler, MessageHandler, Filters,
                          PicklePersistence, Updater, CallbackQueryHandler, PollAnswerHandler)

import inline
from bot_funcs import media_reactor, morning_wisher, bday_wisher, conversation, delete_pin
from bot_funcs.commands import BotCommands as bc
from constants import shanibot
from convos import bday, magic, nick, settings_gui, start
from bot_funcs.quiz import send_quiz, receive_answer, timedout

logging.basicConfig(format='%(asctime)s - %(name)s - %(levelname)s - %(lineno)d - %(message)s', level=logging.INFO)

with open("files/token.txt", 'r') as file:
    shanisir_token, test_token = file.read().split(',')

pp = PicklePersistence(filename='files/user_data')
updater = Updater(token=f'{shanisir_token}', use_context=True, persistence=pp)

dp = updater.dispatcher


def data_view() -> None:
    with open('files/user_data', 'rb') as f:
        pprint.PrettyPrinter(indent=2).pprint(pickle.load(f))


dp.add_handler(InlineQueryHandler(inline.inline_clips))
dp.add_handler(CommandHandler(command='help', callback=bc.helper))
dp.add_handler(CommandHandler(command='secret', callback=bc.secret))
dp.add_handler(CommandHandler(command='start', callback=bc.start))
dp.add_handler(CommandHandler(command='swear', callback=bc.swear))
dp.add_handler(CommandHandler(command='snake', callback=bc.snake))
dp.add_handler(CommandHandler(command='facts', callback=bc.facts))
dp.add_handler(CommandHandler(command='quizizz', callback=bc.quizizz))
dp.add_handler(PollAnswerHandler(callback=receive_answer))

# /8ball conversation-
magicball_handler = ConversationHandler(
    entry_points=[CommandHandler(command="8ball", callback=magic.magic8ball, filters=~Filters.reply),
                  MessageHandler(filters=Filters.command(False) & Filters.regex("8ball") & Filters.reply,
                                 callback=magic.thinking)],

    states={
        magic.PROCESSING: [MessageHandler(filters=Filters.reply & Filters.text, callback=magic.thinking)],

        ConversationHandler.TIMEOUT: [MessageHandler(filters=Filters.all, callback=magic.timedout)]},

    fallbacks=[CommandHandler(command='cancel', callback=magic.cancel)], conversation_timeout=40)
dp.add_handler(magicball_handler)

# /tell conversation-
tell_handler = ConversationHandler(
    entry_points=[CommandHandler('tell', start.initiate)],

    states={
        start.CHOICE: [MessageHandler(filters=Filters.regex("^Birthday$"), callback=bday.bday),
                       MessageHandler(filters=Filters.regex("^Nickname$"), callback=nick.nick),
                       MessageHandler(filters=Filters.regex("^Nothing$"), callback=start.leave)],

        bday.INPUT: [MessageHandler(filters=Filters.regex("^([1-9][0-9]{3}-[0-9]{2}-[0-9]{2})$"),  # Valid date check
                                    callback=bday.bday_add_or_update),
                     MessageHandler(filters=Filters.text, callback=bday.wrong)],  # If it is not a date

        bday.MODIFY: [MessageHandler(filters=Filters.regex("^Forget my birthday sir$"), callback=bday.bday_del),
                      MessageHandler(filters=Filters.regex("^Update my birthday sir$"), callback=bday.bday_mod)],

        nick.SET_NICK: [MessageHandler(filters=Filters.text & Filters.reply, callback=nick.add_edit_nick)],

        nick.MODIFY_NICK: [MessageHandler(filters=Filters.regex("^Change nickname$"), callback=nick.edit_nick),
                           MessageHandler(filters=Filters.regex("^Remove nickname$"), callback=nick.del_nick),
                           MessageHandler(filters=Filters.regex("^Back$"), callback=nick.back)],

        ConversationHandler.TIMEOUT: [MessageHandler(filters=Filters.all, callback=start.timedout)]},

    fallbacks=[MessageHandler(Filters.regex("^No, thank you sir$"), callback=bday.reject),
               CommandHandler("cancel", start.leave)],

    name="/tell convo", persistent=True, allow_reentry=True, conversation_timeout=40)
dp.add_handler(tell_handler)

settings_gui_handler = ConversationHandler(
    entry_points=[CommandHandler('settings', settings_gui.start)],

    states={
        settings_gui.UPDATED: [CallbackQueryHandler(settings_gui.change_prob, pattern="MEDIA_PROB|PROFANE_PROB"),
                               CallbackQueryHandler(settings_gui.morn_swap, pattern="Morning"),
                               CallbackQueryHandler(settings_gui.save, pattern="SAVE")],

        settings_gui.PROBABILITY: [
            CallbackQueryHandler(settings_gui.prob_updater, pattern="0.0|-0.1|-0.05|0.05|0.1|1.0"),
            CallbackQueryHandler(settings_gui.go_back, pattern="Back")]},

    fallbacks=[CommandHandler('cancel', settings_gui.save)])
dp.add_handler(settings_gui_handler)

media_filters = (Filters.document | Filters.photo | Filters.video | Filters.voice | Filters.audio)
edit_filter = Filters.update.edited_message
pin_filter = Filters.status_update.pinned_message

dp.add_handler(MessageHandler(media_filters, media_reactor.media))
dp.add_handler(MessageHandler(pin_filter & Filters.user(username=shanibot), delete_pin.de_pin))
dp.add_handler(MessageHandler(Filters.reply & Filters.group & ~ edit_filter, conversation.reply))
dp.add_handler(MessageHandler(Filters.group & Filters.text & ~ edit_filter, conversation.group))
dp.add_handler(MessageHandler(Filters.private & Filters.text & ~ edit_filter, conversation.shanifier))
dp.add_handler(MessageHandler(Filters.command, bc.unknown))

updater.job_queue.run_repeating(bday_wisher.wish, 86400, first=1)  # Runs every time script is started, and once a day.
updater.job_queue.run_repeating(morning_wisher.morning_goodness, 3600, first=1)
updater.job_queue.run_repeating(inline.get_clips, 60, first=1)  # Have to re-fetch clips since links expire
updater.job_queue.run_repeating(send_quiz, 604800, first=1)  # Send quiz to TMS'20 weekly
updater.job_queue.run_repeating(timedout, 86400, first=20)


data_view()

updater.start_polling()
updater.idle()
