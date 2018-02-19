from telegram.ext import MessageHandler, Filters
from telegram.parsemode import ParseMode

from .dvb_api import departures_for_stop_name, format_departure
from .natural import *


def _message(bot, update):
    intent = parse_intent(update.message.text)
    if intent is None:
        update.message.reply_text('Das habe ich leider nicht verstanden 😕 Aktuell bin ich in der Lage die meisten '
                                  'Fragen nach aktuellen Abfahrtszeiten mit optionaler Angabe einer Linie zu '
                                  'verstehen. Wenn etwas einfach nicht funktionieren will, du dir aber sicher bist, '
                                  'dass das klappen sollte, dann schreib\' bitte @kiliankoe an. Danke 😊')
        return

    if intent.type == Intent.Type.DEPARTURE:
        locations = intent.locations
        if locations is None or len(locations) == 0:
            update.message.reply_text('Ich habe leider nicht verstanden wo du nach aktuellen Abfahrtsinformationen '
                                      'suchst.')
            return

        location = locations[0]
        filter_lines = intent.lines
        if filter_lines is None:
            filter_lines = []

        stop_name, departures = departures_for_stop_name(location, line_filter=filter_lines)
        if len(departures) == 0:
            update.message.reply_text('Da habe ich keine Abfahrten finden können.')
            return

        formatted_departures = '\n'.join([format_departure(dep) for dep in departures[:8]])

        title = f'Abfahrten der *{filter_lines[0]}* für *{stop_name}*' if len(filter_lines) != 0 \
            else f'Abfahrten für *{stop_name}*'

        msg = f'''{title}

```
{formatted_departures}
```
    '''
        update.message.reply_text(msg, parse_mode=ParseMode.MARKDOWN)

    elif intent.type == Intent.Type.LOCATION_SEARCH:
        update.message.reply_text('Meine Erkennung von natürlicher Sprache ist aktuell noch in der Alpha-Phase. '
                                  'Bitte gib\' mir noch eine kleine Weile, bevor ich für dich nach Orten suchen kann.')
    elif intent.type == Intent.Type.ROUTE:
        update.message.reply_text(f'Meine Erkennung von natürlicher Sprache ist aktuell noch in der Alpha-Phase. '
                                  f'Bitte gib\' mir noch eine kleine Weile, bevor ich für dich nach Routen suchen '
                                  f'kann. (route: `{intent.origin}` → `{intent.destination}`)')
    elif intent.type == Intent.Type.DISRUPTIONS:
        update.message.reply_text(f'Meine Erkennung von natürlicher Sprache ist aktuell noch in der Alpha-Phase. '
                                  f'Bitte gib\' mir noch eine kleine Weile, bevor ich für dich nach aktuellen '
                                  f'Störungen suchen kann. (disruption: `{intent.lines}` @ `{intent.locations}`)')


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
