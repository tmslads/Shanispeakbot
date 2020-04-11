# States-
import random as r
from time import sleep

from telegram import ForceReply

from constants import shanibot
from .namer import nicknamer

PROCESSING = range(1)


def magic8ball(update, context):
    """Asks the user for the question."""

    chat_id = update.effective_chat.id
    name = nicknamer(update, context)

    initiate = ["If you have a doubt, just type it here",
                f"{name}, are you confused? Ask me and I'll search for some sow...so..solutions"
                " okay?",
                "I can predict the future like you say . Just ask me. I'm just trying to find you option",
                "Fast fast no time ask me!", "See tell me what's the confusion", f"Yes {name}?"]

    context.bot.send_chat_action(chat_id=chat_id, action='typing')
    sleep(1)
    # Sends message with a force reply
    context.bot.send_message(chat_id=chat_id,
                             text=f"{r.choice(initiate)}🔮\nOr, type /cancel so I won't mind that",
                             reply_markup=ForceReply(force_reply=True, selective=True),
                             reply_to_message_id=update.message.message_id)
    return PROCESSING  # Will go into first (and only) state in convo handler in main.py


def thinking(update, context):
    """
    First sends a message indicating his thinking process for 3 seconds, then on the 4th second he gives the answer
    by editing his message.
    """
    name = nicknamer(update, context)
    chat_id = update.effective_chat.id

    if update.message.reply_to_message.from_user.username != shanibot.replace('@', ''):
        actual_msg = update.message.reply_to_message.message_id

    else:
        actual_msg = update.message.message_id

    thoughts = ["See I'm spending time because your question normally comes mistake", "*scratching nose*",
                "Uhmmm", "Ok, there is one option", "*sniffs*", "What you say like"]

    answers = ["No no I'm sure not", "I don't want to tell you like you say", "I don't know like",
               f"No {name}, I'm so sowry", "Obviously like you say", r"Yes\. No other option like",
               "I didn't say wrong, I don't know", "See just do the worksheet no other importance of the situation",
               "This may be hard, but I think no okay?", "The laws of physics say yes 😄",
               f"Yes yes", "Maybe okay?", "Ah yea", "My feeling says no, now I feel very bad I told you like that",
               "That's not my policy I'm not answering",
               "See don't waste my time like you say with these easy questions okay, fine?",
               f"The universe says yes {name}", "That's going to be broken now", "Sorry no idea"]

    thought = r.choice(thoughts)
    answer = r.choice(answers)
    seconds = list(range(1, 5))

    msg_sent = context.bot.send_message(chat_id=chat_id, text=f"`{thought}`",  # Will be monospaced
                                        parse_mode='MarkdownV2',  # Check Bot API 4.5 for MarkdownV2 docs
                                        reply_to_message_id=actual_msg)

    # Editing message rapidly-
    for second in seconds:
        if second < 4:
            dots = r'\.' * second  # Edits message so the ... (thinking) effect is achieved, \ is an escape seq needed-
            text = rf"`{thought + dots}`"  # for MarkdownV2
        else:
            edit_add = rf'\.\.\.🔮'  # When thinking is done and answer is ready
            text = f"_{answer + edit_add}_"  # Answer will be in italic

        sleep(1)  # So all of this doesn't happen instantly and is visible to user
        context.bot.edit_message_text(chat_id=chat_id, message_id=msg_sent.message_id,
                                      text=f"{text}",  # Edits message sent by bot accordingly
                                      parse_mode='MarkdownV2')

    return -1  # End of conversation


def cancel(update, context):
    """Called when user presses /cancel"""
    context.bot.send_message(chat_id=update.effective_chat.id,
                             text="I just wanted to be in the right direction nothing else I mean okay?",
                             reply_to_message_id=update.message.message_id)

    return -1
