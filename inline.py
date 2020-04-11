from difflib import get_close_matches
from uuid import uuid4

from telegram import InlineQueryResultAudio

from online import util

results = []
links, names = util.clips()

# Adds all clips and names into one list
for clip in zip(links, names):
    results.append(InlineQueryResultAudio(id=uuid4(), audio_url=clip[0], title=clip[1], performer="Shani Sir"))


def inline_clips(update, context):
    query = update.inline_query.query
    if not query:
        context.bot.answer_inline_query(update.inline_query.id, results[:50])  # Show first 49 clips if nothing is typed
    else:
        matches = get_close_matches(query, names, n=15, cutoff=0.3)  # Searches for close matches
        index = 0
        # Bubble sort (kinda) to sort the list according to close matches-
        while index <= len(matches) - 1:
            for pos, result in enumerate(results):
                if index == len(matches):  # Breaks if everything is sorted (to prevent exceptions)
                    break
                if matches[index] == result['title']:
                    results[index], results[pos] = results[pos], results[index]  # Swapping positions if matched
                    index += 1  # Increment by 1 to compare next element

        context.bot.answer_inline_query(inline_query_id=update.inline_query.id,
                                        results=results[:16])  # Show only 15 results
