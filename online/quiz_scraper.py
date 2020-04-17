import random as r
import re
from typing import Tuple, List, Union

import requests
from bs4 import BeautifulSoup

from constants import QUIZ_URL


def a_quiz() -> Union[Tuple[list, List[List[str]], List[int]], None]:
    page = r.randint(1, 76)
    print(page)
    quiz_url = f"{QUIZ_URL}/{page}"
    content = requests.get(quiz_url).content

    soup = BeautifulSoup(content, 'html.parser')
    results = soup.find_all(class_=r.choice(['even', 'odd']))
    all_questions = []
    all_choices = []  # Type: List[List[str(choice)]]
    all_answers = []

    for result in results:
        question_choices = []

        question = result.find('b')  # Get question
        question = question.text.strip()
        question = question[3:]  # Removes the 'Q. ' part

        if len(question) > 255:  # If we've reached max question character limit for ptb
            return

        print(question)
        all_questions.append(question)

        options = result.find_all('br')  # Get options as a list

        if len(options) > 5:  # If there are notes or something weird (cheap way out, but practicality >>)
            options = options[:5]

        for option in options:  # Get string between <br> tags by printing next sibling
            choice = option.nextSibling

            if choice is None:  # Edge case when there's that stupid note
                text = option.text.strip()
                spliced = re.sub('([0-4][)])*', '', text).split()
                question_choices.extend(spliced)
                for one in spliced:  # temporary
                    print(one)
                break

            to_str = str(choice).strip()
            stripped = re.sub('([0-4][)])*', '', to_str).strip()

            if len(stripped) > 100:  # Telegram doesn't allow a choice to have more than 100 characters
                return

            question_choices.append(stripped)
            print(stripped)

        question_choices.pop()  # Remove last empty string

        if len(question_choices) > 10:  # Telegram doesn't allow more than 10 choices
            return

        all_choices.append(question_choices)

        answer = result.find('span', class_='ans')  # Returns answer number
        right_answer = int(answer.text.strip().replace('ANS: ', ''))
        all_answers.append(right_answer - 1)
        print(f'The right answer is: {question_choices[right_answer - 1]}\n\n')

    return all_questions, all_choices, all_answers

#
# questions, choices, answers = a_quiz()
# print(f"{questions}\n{choices}\n{answers}")

# question = questions[0]
# options = choices[0]
# answer = answers[0]
# print(question, options, answer)
