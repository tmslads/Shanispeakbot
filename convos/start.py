from telegram import KeyboardButton, ReplyKeyboardMarkup

keyboard = [
    [KeyboardButton(text="Birthday"), KeyboardButton(text="Secret")],
    [KeyboardButton(text="Nickname"), KeyboardButton(text="Other")],
    [KeyboardButton(text="Nothing")]
]
markup = ReplyKeyboardMarkup(keyboard=keyboard, one_time_keyboard=True)

CHOICE = range(1)


def initiate(update, context):  # Entry_point
    name = update.message.from_user.first_name

    context.bot.send_message(chat_id=update.effective_chat.id, text=f'What do you want to tell me {name}?',
                             reply_to_message_id=update.message.message_id, reply_markup=markup)
    return CHOICE


def leave(update, context):
    name = update.message.from_user.first_name

    context.bot.send_message(chat_id=update.effective_chat.id,
                             text=f'Bye {name}, sit and solve the past papers like you say, I want to put a test okay?',
                             reply_to_message_id=update.message.message_id)

    return -1
