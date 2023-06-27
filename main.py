import logging
import os
import re
import xml.etree.ElementTree as ET

import telebot as tb

logger = tb.logger
logger.setLevel(logging.INFO)

API_TOKEN = os.environ.get('PAVLIK_API_TOKEN')
if not API_TOKEN:
    logger.fatal('Telegram Bot API Token is not defined in environment variables')
    exit(1)

bot = tb.TeleBot(API_TOKEN)


def similar(query, quote):
    for query_word in query:
        for quote_word in re.findall(r'\w+', quote.lower()):
            if query_word.lower() in quote_word:
                return True
    return False


def get_quotes(query):
    queried_words = query.lower().split()
    quotes = []

    tree = ET.parse('quotes.xml')
    resources = tree.getroot()

    i = 0
    for season in resources:
        for episode in season:
            for quote in episode:
                quote_text = quote.attrib['desc']
                if similar(queried_words, quote_text):
                    file_id = quote.attrib['file_id']
                    result = tb.types.InlineQueryResultCachedVoice(i, file_id, quote_text)
                    quotes.append(result)
                    i += 1

    return quotes


@bot.inline_handler(lambda query: len(query.query) >= 0)
def query_text(inline_query):
    try:
        quotes = get_quotes(inline_query.query)
        if quotes:
            bot.answer_inline_query(inline_query.id, quotes)
    except Exception as e:
        logger.error(e)


@bot.message_handler(content_types=['voice'])
def get_file_id(m):
    msg = m.voice.file_id
    logger.info(msg)


bot.infinity_polling()
