import random as r
import re
from typing import List, Union, Tuple

import requests
from bs4 import BeautifulSoup

from constants import QUIZ_URL
from helpers.logger import logger


def quiz_maker_v2(number: int) -> Tuple[List[str], List[List[str]], List[int]]:
    """
    Scrapes a random page to get all questions, and returns 3 lists, one which contains only questions,
    another one contains choices for each of the questions, and the last one contains answers which are indexes
    (points to correct option).

    Args:
        number (:obj:`int`): The number of question(s) (with respective choices and answers) to return. Must be between
            1 and 10 (both included).
    """

    def remover():
        """Helper function to remove respective question, choice and answer."""
        try:
            all_questions.remove(question)
            all_choices.remove(choices)
            all_answers.remove(answer)
        except ValueError:
            pass

    page = r.randint(1, 76)
    logger(message=f"Quiz obtained from {page=}.")
    quiz_url = f"{QUIZ_URL}/{page}"

    soup = BeautifulSoup(requests.get(quiz_url).content, 'lxml')
    results_ques = soup.find_all(class_=lambda a_class: a_class == 'odd' or a_class == 'even')

    all_questions = []
    all_choices = []  # Type: List[List[str(choices)]]
    all_answers = []

    for result in results_ques:
        ops = result.find_all(['br', 'sup', 'sub'])
        question_choices = []

        if len(ops) == 5:
            ops.pop()

        if result.b.string is not None:
            question = str(result.b.string)
        else:
            if result.i is not None:  # If there are italics in question
                question = str(result.b.get_text())  # Get text without italics
            else:
                question = str(result.b.next_element.string)

        all_questions.append(question[3:].strip())  # [3:] is to remove 'Q. '

        option = ''  # String to add choices
        for op in ops:  # Loop through choices if extra formatting such as subscripts or superscripts are present

            sub_sup = re.sub('([0-9][)] )*', '', op.next_element.string).strip()  # Remove choice numbers like '1 )'
            if op.name == 'sup':  # If superscript present, add that
                option += u''.join(dict(zip(u"-0123456789", u"⁻⁰¹²³⁴⁵⁶⁷⁸⁹")).get(c, c) for c in sub_sup)
            elif op.name == 'sub':  # If subscript present, add that
                option += u''.join(dict(zip(u"-0123456789", u"₋₀₁₂₃₄₅₆₇₈₉")).get(c, c) for c in sub_sup)
            else:  # If normal text, just add that
                option += sub_sup

            sib = op.next_sibling
            if sib.string is not None:
                stripped = re.sub('([0-9][)] )*', '', sib.string).strip()
                if stripped != sub_sup:  # Checks if already similar to what's already added or not
                    option += sib
            if sib.next_element.name in ('br', None):  # When we've reached end of question and its choices
                question_choices.append(option.strip())  # Add choice
                option = ''  # Reset choice for next choice

        if question_choices[-1] == "Note:":  # Remove notes (not needed)
            question_choices.pop()

        all_choices.append(question_choices)  # Add all the choices for the respective question
        all_answers.append(int(result.span.get_text()[6:]) - 1)  # Add answer index, [6:] is to remove 'ANS: '

    # Filter questions and choices for Telegram limits (max 10 choices, each choice < 100 chars, question < 255 chars)
    for question, choices, answer in zip(all_questions[:], all_choices[:], all_answers[:]):
        for choice in choices:
            # Question's formatting (sub/sup) gets into the choices so we have to add that to the question-
            if choice[0] in dict(zip('⁻⁰¹²³⁴⁵⁶⁷⁸⁹₀₁₂₃₄₅₆₇₈₉', '-01234567890123456789')):
                all_questions[all_questions.index(question)] = question + choice  # Add to question
                choices.remove(choice)  # Remove that choice from list since it's in the question
            if len(choice) > 100:
                remover()
                break
        else:
            if len(question) > 255 or len(choices) > 10:
                remover()

    return tuple(zip(*r.sample(list(zip(all_questions, all_choices, all_answers)), k=number)))  # Get random question(s)
