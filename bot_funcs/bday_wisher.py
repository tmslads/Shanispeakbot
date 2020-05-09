from datetime import datetime, date

from telegram.ext import CallbackContext

from constants import group_ids
from helpers.logger import logger
from online import gcalendar


def wish(context: CallbackContext) -> None:
    """Gets the next birthday from Google Calendar and wishes you if today is your birthday."""

    gcalendar.main()
    days_remaining, name = gcalendar.get_next_bday()

    bday_msgs = [f"Happy birthday {name}! !🎉 I don't know why like, but I know you despise me with the burning "
                 f"passion of a thousand suns. I don't give a flux, like you say. I implore you to let go of "
                 f"hate and embrace love. Spend the rest of your days with love in your heart and faith in your "
                 f"soul. Life's cyclotron may sometimes send you tumbling around, but remember that it is "
                 f"necessary to do so in order to hit the targit. Negative emotions act as charge for the "
                 f"velocity selector of life. Remove them from your being and you shall not stray from the "
                 f"straight path. I wish you the best. May your jockeys be unpressed and your apertures small. "
                 f"Enjoy your 18th. Forget about coronabitch. Godspeed.",

                 f"Happy birthday {name}! I wish you the best of luck for life. Remember: You matter. Until you "
                 f"multiply yourself times the speed of light squared. Then you energy, like you say!🎉 What "
                 f"your going to do today like?",

                 f"Happy birthday {name}! !🎉 What your going to do today like?"]

    _12B = group_ids['12b']

    # Wishes from Google Calendar-
    if days_remaining == 0:
        msg = context.bot.send_message(chat_id=_12B, text=bday_msgs[0])
        context.bot.pin_chat_message(chat_id=_12B, message_id=msg.message_id, disable_notification=True)
        logger(message=f"Happy birthday message to {name} was just sent.")

        now = str(date.today())
        today = datetime.strptime(now, "%Y-%m-%d")  # Parses today's date (time object) into datetime object
        new_date = today.replace(year=today.year + 1)

        gcalendar.CalendarEventManager(name=name).update_event(new_date)  # Updates bday to next year

    # TODO: Wishes from /tell birthday input-
