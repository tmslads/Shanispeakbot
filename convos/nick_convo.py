from start import markup, CHOICE
from telegram import ForceReply
from telegram import KeyboardButton
from telegram import ReplyKeyboardMarkup

SET_NICK, MODIFY_NICK = range(3, 5)


def nick(update, context):
    name = update.message.from_user.first_name

    if 'nickname' not in context.user_data or context.user_data['nickname'] == name:
        context.bot.send_message(chat_id=update.effective_chat.id,
                                 text="What is your uhh what you say like ni...nick..nickname?",
                                 reply_to_message_id=update.message.message_id, reply_markup=ForceReply(selective=True))

        return SET_NICK

    else:
        nick_kb = [[KeyboardButton("Change nickname"), KeyboardButton("Remove nickname")],
                   [KeyboardButton("Back")]]

        nick_markup = ReplyKeyboardMarkup(nick_kb, one_time_keyboard=True)
        nick_name = context.user_data["nickname"]
        context.bot.send_message(chat_id=update.effective_chat.id,
                                 text=f"Hi {nick_name}, what you want to do like?", reply_markup=nick_markup,
                                 reply_to_message_id=update.message.message_id)

        return MODIFY_NICK


def del_nick(update, context):  # MODIFY_NICK
    user_id = update.message.from_user.id
    name = update.message.from_user.first_name

    context.user_data['nickname'] = name
    context.bot.send_message(chat_id=update.effective_chat.id,
                             text=f"I'm forgetting your nic.. {name}",
                             reply_to_message_id=update.message.message_id,
                             reply_markup=markup)
    return CHOICE


def edit_nick(update, context):  # MODIFY_NICK
    context.bot.send_message(chat_id=update.effective_chat.id,
                             text=f"What is your like you say new nickname?",
                             reply_to_message_id=update.message.message_id, reply_markup=ForceReply(selective=True))
    return SET_NICK


def add_edit_nick(update, context):  # SET_NICK

    context.user_data['nickname'] = update.message.text
    nicky = context.user_data['nickname']
    context.bot.send_message(chat_id=update.effective_chat.id,
                             text=f"Hi {nicky} what you're doing like",
                             reply_to_message_id=update.message.message_id, reply_markup=markup)
    return CHOICE


def back(update, context):  # MODIFY_NICK
    context.bot.send_message(chat_id=update.effective_chat.id,
                             text=f"What you want?",
                             reply_to_message_id=update.message.message_id,
                             reply_markup=markup)
    return CHOICE
