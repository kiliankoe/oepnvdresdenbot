import json
import os

import requests
from telegram.ext import MessageHandler, Filters
from telegram.parsemode import ParseMode

from .dvb_api import departures_for_stop_name, format_departure


def _message(bot, update):
    intent_res = _read_intent(update.message.text)
    entities = intent_res.get('entities')
    intents = entities.get('intent')
    if intents is None or len(intents) == 0:
        update.message.reply_text('Das habe ich leider nicht verstanden 😕')
        return

    intent = intents[0].get('value')

    if intent == 'departure':
        locations = entities.get('location')
        if locations is None or len(locations) == 0:
            update.message.reply_text('Ich habe leider nicht verstanden wo du nach aktuellen Abfahrtsinformationen '
                                      'suchst.')
            return
        location = locations[0].get('value')

        lines = entities.get('line_identifier')
        if lines is None or len(lines) == 0:
            filter_lines = []
        else:
            filter_lines = [l['value'] for l in lines]

        stop_name, departures = departures_for_stop_name(location, line_filter=filter_lines)
        if len(departures) == 0:
            update.message.reply_text('Da habe ich keine Abfahrten finden können.')
            return

        formatted_departures = '\n'.join([format_departure(dep) for dep in departures[:8]])

        title = f'Abfahrten der {filter_lines[0]} für *{stop_name}*' if len(filter_lines) != 0 \
            else f'Abfahrten für *{stop_name}*'

        msg = f'''{title}

```
{formatted_departures}
```
    '''
        update.message.reply_text(msg, parse_mode=ParseMode.MARKDOWN)

    elif intent == 'search':
        update.message.reply_text('Das habe ich leider nicht verstanden, entschuldige.')
    elif intent == 'location_search':
        update.message.reply_text('Das habe ich leider nicht verstanden, entschuldige.')
    elif intent == 'route':
        update.message.reply_text('Aktuell kann ich leider noch nicht nach Routen suchen. Aber sehr sehr bald, '
                                  'versprochen! ✌️')


def _read_intent(text: str) -> dict:
    response = requests.get(
        url='https://api.wit.ai/message',
        params=dict(v='20180218', q=text),
        headers=dict(Authorization='Bearer {}'.format(os.getenv('WITAI_SERVER_ACCESS_TOKEN'))),
    )
    if response.status_code != 200:
        return {}
    return json.loads(response.text)


message_handler = MessageHandler(Filters.text, _message)
