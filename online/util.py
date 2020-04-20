import re

import requests
from bs4 import BeautifulSoup, SoupStrainer
from typing import Tuple

from constants import LINK, FACT_URL

with open('creds/github_token.txt', 'r') as f:
    token = f.read()

header = {'Authorization': f'token {token}', 'token_type': 'bearer'}


def clips() -> Tuple[list, list]:
    """Extracts the download links and names from the Shanisirmodule using the Github API."""

    dl_links = []
    names = []
    getting = requests.get(LINK, headers=header).json()

    for result in getting:
        url = result['download_url']
        name = result['name'][:-4]
        if url is not None:
            dl_links.append(url)
            names.append(name)

    return dl_links, names


def facts() -> list:
    """Return list of three facts"""

    page = requests.get(FACT_URL)
    results = BeautifulSoup(page.content, 'html.parser', parse_only=SoupStrainer(id='z'))  # Get only z tags
    facts_list = [str(results.contents[index].contents[0]) for index in range(len(results))]

    return facts_list
