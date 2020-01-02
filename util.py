import requests
import re
from bs4 import BeautifulSoup

_DOWNLOAD = "https://raw.githubusercontent.com"
_LINK = "https://github.com/tmslads/Shanisirmodule/tree/haunya/Assets/clips"
URL = 'http://randomfactgenerator.net/'  # To be scraped for facts()
dl_links = []
names = []

getting = requests.get(_LINK)
scraped = BeautifulSoup(getting.content, 'html.parser')
results = scraped.find_all(href=re.compile('/tmslads/Shanisirmodule/blob/haunya/Assets/clips/'))


def clips():
    for index, result in enumerate(results):
        url = f"{_DOWNLOAD}{result['href'].replace('blob/', '')}"
        name = result['title'][:-4]
        dl_links.append(url)
        names.append(name)
    return dl_links, names


def facts():
    page = requests.get(URL)
    soup = BeautifulSoup(page.content, 'html.parser')
    final = soup.find_all(id='z')  # Finds HTML elements with ID 'z'
    return final
