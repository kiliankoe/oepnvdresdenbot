from datetime import datetime, timedelta
import logging

from dvb import Departure, Stop
from telegram.ext import CommandHandler
from telegram.parsemode import ParseMode

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

    if stop_query in stop_id_cache:
        logging.debug(f'Found {stop_query} in cache.')
        stop = stop_id_cache[stop_query]
    else:
        logging.debug(f'{stop_query} not in cache. Fetching id.')
        stop_res = Stop.find(stop_query)
        if len(stop_res.get('stops')) == 0:
            update.message.reply_text('Keine solche Haltestelle gefunden.')
            return
        stop = stop_res['stops'][0].id
        stop_id_cache[stop_query] = stop

    now = datetime.now()
    date_offset = now + timedelta(minutes=offset)

    departure_res = Departure.for_stop(stop, time=date_offset)
    departures = departure_res['departures'][:10]

    if len(departures) == 0:
        update.message.reply_text('Keine Abfahrten gefunden.')
        return

    joined_departures = '\n'.join([_format_departure(dep) for dep in departures])
    msg = f'''Abfahrten *{departure_res["name"]}*
    
```
{joined_departures}
```
    '''

    update.message.reply_text(msg, parse_mode=ParseMode.MARKDOWN)


def _format_departure(dep: Departure) -> str:
    line = dep.line_name.ljust(5)
    direction = dep.direction.ljust(17)
    eta = dep.fancy_eta()

    if eta == 0:
        eta = ''

    return f'{line} {direction} {eta}'


monitor_handler = CommandHandler('abfahrten', _monitor_cmd, pass_args=True)
monitor_shorthand_handler = CommandHandler('a', _monitor_cmd, pass_args=True)
