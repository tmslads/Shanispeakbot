from datetime import datetime, date

from telegram.ext import CallbackContext
from telegram.utils.helpers import mention_html

from constants import group_ids, class_12b
from helpers.logger import logger
from online import gcalendar


def wish(context: CallbackContext) -> None:
    """Gets the next birthday from Google Calendar and wishes you if today is your birthday."""

    gcalendar.main()
    bdays = gcalendar.get_next_bday()
    days_remaining = bdays[0][0]

    bday_msgs = (f"Happy birthday (placeholder)! !🎉 I don't know why like, but I know you despise me with the burning "
                 f"passion of a thousand suns. I don't give a flux, like you say. I implore you to let go of "
                 f"hate and embrace love. Spend the rest of your days with love in your heart and faith in your "
                 f"soul. Life's cyclotron may sometimes send you tumbling around, but remember that it is "
                 f"necessary to do so in order to hit the targit. Negative emotions act as charge for the "
                 f"velocity selector of life. Remove them from your being and you shall not stray from the "
                 f"straight path. I wish you the best. May your jockeys be unpressed and your apertures small. "
                 f"Enjoy your 18th. Forget about coronabitch. Godspeed.",

                 f"Happy birthday (placeholder)! I wish you the best of luck for life. Remember: You matter. Until you "
                 f"multiply yourself times the speed of light squared. Then you energy, like you say!🎉 What "
                 f"your going to do today like?",

                 f"Happy birthday (placeholder)! !🎉 What your going to do today like?")

    # Wishes from Google Calendar-
    if days_remaining == 0:
        _12B = group_ids['12b']

        now = str(date.today())
        today = datetime.strptime(now, "%Y-%m-%d")  # Parses today's date (time object) into datetime object
        new_date = today.replace(year=today.year + 1)

        for _, name in bdays:
            try:
                mention = mention_html(class_12b[name.capitalize()], name)
            except KeyError:  # For those fools who don't use Telegram :(
                mention = name

            msg = context.bot.send_message(chat_id=_12B, text=bday_msgs[2].replace('(placeholder)', mention),
                                           parse_mode="HTML")
            context.bot.pin_chat_message(chat_id=_12B, message_id=msg.message_id, disable_notification=True)
            logger(message=f"Happy birthday message for {name} was just sent to the 12B group.")
            gcalendar.CalendarEventManager(name=name).update_event(new_date)  # Updates bday to next year

        context.bot.send_message(chat_id=_12B, text="🎂")  # Animated cake emoji :)
        del _12B, now, today, new_date

    elif days_remaining in {21, 69}:
        for _, name in bdays:
            context.bot.send_message(chat_id=group_ids['12b'], text=f"{name}'s birthday is in {days_remaining} days!!")
            logger(message=f"Happy birthday reminder for {name}({days_remaining} days) was just sent to the 12B group.")

    del days_remaining, bdays, bday_msgs
