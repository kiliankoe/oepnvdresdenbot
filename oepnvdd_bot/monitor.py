from datetime import datetime, timedelta

import pytz
from telegram.ext import CommandHandler
from telegram.parsemode import ParseMode

from .dvb_api import departures_for_stop_name, format_departure

stop_id_cache = dict()


def _monitor_cmd(bot, update, args):
    if len(args) == 0:
        update.message.reply_text('Für welche Haltestelle soll ich nach kommenden Abfahrten suchen? Hier ein paar '
                                  'Nutzungsbeispiele:\n\n'
                                  '/abfahrten Albertplatz - Die nächsten Abfahrten am Albertplatz\n'
                                  '/abfahrten Postplatz 10 - Die nächsten Abfahrten am Postplatz in mind. 10 Minuten\n'
                                  '/a Hauptbahnhof - /a ist kurz für /abfahrten und funktioniert exakt gleich')
        return

    offset = 0
    stop_query = ' '.join(args)
    if len(args) > 1 and args[-1].isdigit():
        offset = int(args[-1])
        stop_query = ' '.join(args[:-1])

    tz = pytz.timezone('Europe/Berlin')
    now = datetime.now(tz=tz)  # explicitly pass correct timezone for Dresden
    date_offset = now + timedelta(minutes=offset)

    stop_name, departures = departures_for_stop_name(stop_query, time=date_offset)
    departures = departures[:8]

    if len(departures) == 0:
        update.message.reply_text('Keine Abfahrten gefunden.')
        return

    joined_departures = '\n'.join([format_departure(dep) for dep in departures])
    offset_str = f'in {offset} Minuten' if offset != 0 else ''

    msg = f'''Abfahrten für *{stop_name}* {offset_str}
    
```
{joined_departures}
```
    '''

    update.message.reply_text(msg, parse_mode=ParseMode.MARKDOWN)


monitor_handler = CommandHandler('abfahrten', _monitor_cmd, pass_args=True)
monitor_shorthand_handler = CommandHandler('a', _monitor_cmd, pass_args=True)
