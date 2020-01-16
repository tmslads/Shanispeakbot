from difflib import get_close_matches
from uuid import uuid4

from telegram import InlineQueryResultAudio

import util

results = []
links, names = util.clips()

for clip in zip(links, names):
    results.append(InlineQueryResultAudio(id=uuid4(),
                                          audio_url=clip[0], title=clip[1], performer="Shani Sir"))


def inline_clips(update, context):
    query = update.inline_query.query
    if not query:
        context.bot.answer_inline_query(update.inline_query.id, results[:50])
    else:
        matches = get_close_matches(query, names, n=15, cutoff=0.3)
        index = 0
        while index <= len(matches) - 1:
            for pos, result in enumerate(results):
                if index == len(matches):
                    break
                if matches[index] == result['title']:
                    results[index], results[pos] = results[pos], results[index]
                    index += 1

        context.bot.answer_inline_query(inline_query_id=update.inline_query.id, results=results[:16])
