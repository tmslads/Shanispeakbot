import re

import requests
from bs4 import BeautifulSoup
from typing import Tuple

from constants import _LINK, _DOWNLOAD, URL

dl_links = []
names = []

getting = requests.get(_LINK)
scraped = BeautifulSoup(getting.content, 'html.parser')
results = scraped.find_all(href=re.compile('/tmslads/Shanisirmodule/blob/master/Assets/clips/'))


def clips() -> Tuple[list, list]:
    for index, result in enumerate(results):
        url = f"{_DOWNLOAD}{result['href'].replace('blob/', '')}"
        name = result['title'][:-4]
        dl_links.append(url)
        names.append(name)
    return dl_links, names


def facts() -> list:
    """Return list of three facts"""
    page = requests.get(URL)
    soup = BeautifulSoup(page.content, 'html.parser')
    result = soup.find_all(id='z')  # Finds HTML elements with ID 'z'
    facts_list = [result[0].getText()[:-6], result[1].getText()[:-6],
                  result[2].getText()[:-6]]
    return facts_list
