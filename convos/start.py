from telegram import KeyboardButton, ReplyKeyboardMarkup, ReplyKeyboardRemove

# This is the main menu. Shown when /tell is invoked.

keyboard = [
    [KeyboardButton(text="Birthday"), KeyboardButton(text="Nickname")],
    [KeyboardButton(text="Nothing")]
]
markup = ReplyKeyboardMarkup(keyboard=keyboard, one_time_keyboard=True)

CHOICE = range(1)


def nicknamer(update, context):
    try:
        name = context.user_data['nickname'][-1]
    except (KeyError, IndexError):
        context.user_data['nickname'] = []
        context.user_data['nickname'].append(update.message.from_user.first_name)
    finally:
        return context.user_data['nickname'][-1]


def initiate(update, context):  # Entry_point
    name = nicknamer(update, context)

    context.bot.send_message(chat_id=update.effective_chat.id, text=f'What do you want to tell me {name}?',
                             reply_to_message_id=update.message.message_id, reply_markup=markup)
    return CHOICE


def leave(update, context):
    name = nicknamer(update, context)

    context.bot.send_message(chat_id=update.effective_chat.id,
                             text=f'Bye {name}, sit and solve the past papers like you say, I want to put a test okay?',
                             reply_to_message_id=update.message.message_id,
                             reply_markup=ReplyKeyboardRemove(selective=True))

    return -1
