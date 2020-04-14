import logging
import os
import pprint
import random as r
from threading import Timer

import numpy as np
from PIL import Image, ImageDraw
from matplotlib import patheffects
from matplotlib import pyplot as plt
from matplotlib.cbook import get_sample_data
from matplotlib.offsetbox import (OffsetImage, AnnotationBbox)
from telegram import Poll, ParseMode
from telegram.ext.dispatcher import run_async
from telegram.utils.helpers import mention_html

from helpers.namer import get_nick
from online import quiz_scraper

quizzes = []
cwd = os.getcwd()

logging.basicConfig(format='%(asctime)s - %(module)s - %(levelname)s - %(lineno)d - %(message)s', level=logging.INFO)


@run_async  # Have to run it asynchronously as we are using Timer() objects in function.
def send_quiz(update, context):
    global quizzes  # Bad practice to do this with @run_async

    # TODO: Remove my reset-
    context.bot_data['quizizz'][476269395]['answers_right'] = 0
    context.bot_data['quizizz'][476269395]['questions_answered'] = 0
    context.bot_data['quizizz'][476269395]['answers_wrong'] = 0

    while True:
        try:
            questions, choices, answers = quiz_scraper.a_quiz()
            break
        except TypeError:  # If we get None (due to error) back, retry.
            pass

    # Support sending quiz to 12B only for now-
    # TODO: Change this back to 12B
    for question, choice, answer in zip(questions, choices, answers):
        quiz = context.bot.send_poll(chat_id=update.effective_chat.id, question=question, options=choice,
                                     is_anonymous=False, type=Poll.QUIZ, correct_option_id=answer, is_closed=False)
        quizzes.append(quiz)
    logging.info(f"\nThe 5 quizzes were just sent to 12B successfully.\n\n")
    # # TODO: Add message that you have only 24 hours to answer quiz.
    time_limit = Timer(60 * 30, timedout, args=[update, context, quizzes])  # 10 for testing purposes
    time_limit.start()
    time_limit.join()


def timedout(update, context, array):
    """Closes quiz when the time limit is over."""

    to_scold = []
    scolds = ["See if this is troubling you, you can come and get help from me directly okay?",
              "Now I didn't expect thaaat level. See this is counted for the term exam okay",
              "This is for you okay? This is for you to see your level. Aim to hit the tarjit",
              "It's not that hard I expected something but I didn't know this level",
              "You have to write retest no other option like you say",
              "I'm just trying to find you option keep in mind you have any other option keep in mind like",
              "This is like you say embarrassing to me. You have to put effort and work towards the boards now",
              "That's it. I am telling mudassir sir now. Just tell me what's the confusion.",
              "Are you fine? Physics is easy what's the problem like",
              "You are troubling me. See I just wanted to be in the right direction nothing else I mean okay?"]

    scold_names = ""
    chat_id = update.effective_chat.id

    for index, quiz in enumerate(array):  # Stop all quizzes
        context.bot.stop_poll(chat_id=chat_id, message_id=quiz.message_id)

    context.bot.send_chat_action(chat_id=chat_id, action='upload_photo')

    leaderboard(context)  # Show leaderboard

    context.bot.send_photo(chat_id=chat_id, photo=open('leaderboard.png', 'rb'),
                           caption="This is where you stand like you say")  # Send latest leaderboard
    logging.info("\nThe leaderboard was just sent on the group.\n\n")

    context.bot.send_chat_action(chat_id=chat_id, action='typing')

    # Get user mentions of people who got 3 or more answers wrong and scold them-
    for user_id, value in context.bot_data['quizizz'].items():
        if value['answers_wrong'] >= 3:
            name = value['name']
            to_scold.append((user_id, name))
        del value['answers_wrong']  # Reset answers_wrong for every quiz

    for name in to_scold:
        mention = mention_html(user_id=name[0], name=name[1])  # Get their mention in html
        scold_names += mention + " "  # Add a whitespace after every name

    context.bot.send_message(chat_id=chat_id, text=scold_names + r.choice(scolds), parse_mode=ParseMode.HTML)


def receive_answer(update, context):
    user = update.poll_answer.user
    chosen_answer = update.poll_answer.option_ids
    correct_answer = None

    for quiz in quizzes:
        if quiz.poll.id == update.poll_answer.poll_id:
            correct_answer = quiz.poll.correct_option_id
            chat_id = quiz.chat.id
            break
    else:  # Only happens when /quizizz quiz was answered.
        return

    assert correct_answer is not None

    if 'quizizz' not in context.bot_data:
        context.bot_data['quizizz'] = {}

    if user.id not in context.bot_data['quizizz']:
        context.bot_data['quizizz'][user.id] = {'answers_right': 0, 'questions_answered': 0,
                                                'name': get_nick(update, context), 'profile_pic': pp(update, context)}

    else:  # Update entries if changed
        context.bot_data['quizizz'][user.id]['name'] = get_nick(update, context)
        context.bot_data['quizizz'][user.id]['profile_pic'] = pp(update, context)

    guy = context.bot_data['quizizz'][user.id]

    if correct_answer != chosen_answer[0]:
        if 'answers_wrong' not in guy:
            guy['answers_wrong'] = 1
        else:
            guy['answers_wrong'] += 1
    else:
        context.bot_data['quizizz'][user.id]['answers_right'] += 1

    context.bot_data['quizizz'][user.id]['questions_answered'] += 1
    pprint.PrettyPrinter(indent=2).pprint(context.bot_data)


def pp(update, context):
    """Helper function to get a user's profile pic. This will be then used in the bar graph."""

    user = update.poll_answer.user
    pic = context.bot.get_user_profile_photos(user_id=user.id, offset=0, limit=1)

    if not pic:  # If user doesn't have a pp
        return "profile_pics/nobody.jpg"

    first_pic = pic.photos[0][0]
    file_id = first_pic.file_id

    file = context.bot.get_file(file_id=file_id)
    return file.download(custom_path=f"profile_pics/{get_nick(update, context)}.jpg")  # Returns file path as string


def round_pic():
    # Open the input image as numpy array, convert to RGB
    for name in os.listdir(f"{cwd}/profile_pics"):

        if name in ("nobody.png", "trophy.png"):
            continue

        img = Image.open(f"profile_pics/{name}").convert("RGB")
        npImage = np.array(img)
        h, w = img.size

        # Create same size alpha layer with circle
        alpha = Image.new('L', img.size, 0)
        draw = ImageDraw.Draw(alpha)
        draw.pieslice([0, 0, h, w], 0, 360, fill=255)

        # Convert alpha Image to numpy array
        npAlpha = np.array(alpha)

        # Add alpha layer to RGB
        npImage = np.dstack((npImage, npAlpha))

        png_name = name.replace('jpg', 'png')
        jpg_name_path = f"{cwd}/profile_pics/{name}"

        # Save with alpha
        Image.fromarray(npImage).save(f"profile_pics/{png_name}")  # Only saves in .png
        os.remove(jpg_name_path)  # Remove jpg file
        print("DOne")


def add_image(name, x, y, offset=1.6, zoom=0.23):
    # Open image as numpy array-
    with get_sample_data(f"{cwd}/profile_pics/{name}.png") as file:
        arr_img = plt.imread(file, format='jpg')

    image_box = OffsetImage(arr_img, zoom=zoom)  # zoom changes the size of the image

    # Adds image to the provided coordinates-
    return AnnotationBbox(image_box, (x + offset, y), frameon=False, annotation_clip=False)


def leaderboard(context):
    round_pic()  # Make sure all pics are round before starting

    names, vals = [], []

    for stuff in context.bot_data['quizizz'].values():
        names.append(stuff['name'])
        vals.append(stuff['answers_right'])

    # names = ["Harshil", "Samir", "Sahil", "Samrin", "Ashwin", "Jaden"]
    # vals = [21, 18, 10, 5, 17, 9]

    mean = sum(vals) / len(vals)  # Gets average for color sorting later
    vals, names = zip(*sorted(zip(vals, names)))  # Sorts both lists correspondingly in ascending order

    canvas, ax = plt.subplots(1, 1, figsize=(10, 8))  # That figsize is needed as we are putting pics too (10,8)
    plt.grid()  # Shows grid lines

    ax.set_axisbelow(True)  # Makes grid lines go behind bars
    canvas.patch.set_facecolor("#20124d")  # Purple color as background
    ax.patch.set_facecolor("#20124d")  # and for the graph too!

    barlist = ax.barh(y=list(names), width=list(vals), height=0.4,
                      linewidth=1, edgecolor='white',
                      path_effects=[patheffects.SimpleLineShadow(shadow_color='#331C7C', alpha=0.8),
                                    patheffects.Normal()])  # Makes bar graph with shadows

    # for loop to adjust bar color and add arrows, correct answers and profile pics next to the bar-
    for (index, bar), name in zip(enumerate(barlist), names):

        marks = bar.get_width()  # Get no. of correct answers of that guy

        if index == 0:
            size = 16
            effects = [patheffects.SimpleLineShadow(shadow_color='black', alpha=0.9),
                       patheffects.Normal()]
            ab = add_image("trophy", marks, index, offset=-1.8, zoom=0.04)
            ax.add_artist(ab)  # Draws annotation
        else:
            size = 13
            effects = None

        if marks > mean:
            color = '#00FA3F'
            barlist[index].set_color(color)  # Set bar color to green if guy got above avg marks
        elif marks <= mean - 10:
            color = "#FA1D07"
            barlist[index].set_color(color)  # Set bar color to red if guy got really bad marks
        else:
            color = "#F8ED0F"
            barlist[index].set_color(color)  # Set bar color to yellow if guy got below avg marks

        plt.arrow(marks + 0.7, index, -0.001, 0, head_width=0.25, color='#02D4F5')  # Adds left pointing blue arrow
        plt.text(marks - 0.6, index, str(marks), color="#000000", verticalalignment='center',
                 fontdict={'weight': 'demibold', 'size': size, 'fontfamily': 'DejaVu Sans'}, ha='center',
                 alpha=0.7, path_effects=effects)  # Puts marks on the bars near the end

        ab = add_image(name, marks, index)
        ax.add_artist(ab)

    plt.xticks(range(0, max(vals) + 1, 5), fontweight='demi', fontfamily='DejaVu Sans')  # Set scale to 5
    plt.yticks(range(len(names)), names, fontweight='demi', fontstretch='condensed', fontfamily='DejaVu Sans',
               fontvariant='small-caps', fontsize=13)  # Changes look of names
    plt.ylim(top=len(vals) - 0.6)  # Slightly cut off axis at the end for aesthetic purposes

    # Remove the 'box' like look of graph-
    ax.spines['top'].set_visible(False)
    ax.spines['right'].set_visible(False)
    ax.spines['bottom'].set_linewidth(0.01)
    ax.spines['left'].set_visible(0.9)

    # Set color to white for aesthetic purposes-
    ax.spines['left'].set_color("#FFFFFF")
    ax.spines['bottom'].set_color("#FFFFFF")

    # Change grid line properties for both x and y axis aesthetic purposes-
    ax.tick_params(axis='x', grid_alpha=1, colors='#dcd5f4', direction='inout', grid_color='#382a65',
                   grid_linewidth=1.7)
    ax.tick_params(axis='y', colors='#dcd5f4', grid_alpha=0.0)

    # Set title and add properties to make it a beaut
    plt.title(label="LEADERBOARD", fontdict={'fontname': 'Gill Sans MT', 'size': 23, 'weight': 'bold',
                                             'color': '#f3c977'}, loc='left', pad=20,
              path_effects=[patheffects.Stroke(linewidth=0.1, foreground="#F4C05B"),
                            patheffects.Normal()])

    # Add only x axis label and then adjust it to look good.
    plt.xlabel(xlabel="Correct answers", fontdict={'size': 14, 'color': '#d6d0ec', 'weight': 'semibold'}, labelpad=18)

    plt.savefig("leaderboard.png", facecolor="#20124d")  # Save figure with same 'purple' fig color

    for name in os.listdir(f"{cwd}/profile_pics"):
        if name not in ("nobody.png", "trophy.png"):
            os.remove(f"{cwd}/profile_pics/{name}")

    return
    # plt.show()

# leaderboard()
# round_pic()
