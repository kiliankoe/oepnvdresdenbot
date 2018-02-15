import dvb
from telegram.ext import CommandHandler
from telegram.parsemode import ParseMode


def _monitor_cmd(bot, update, args):
    stop = ' '.join(args)
    departures = dvb.monitor(stop)

    if len(departures) == 0:
        update.message.reply_text('Keine Abfahrten gefunden.')
        return

    joined_departures = '\n'.join([_format_departure(dep) for dep in departures])
    msg = f'''*Abfahrten {stop}*
    
```
{joined_departures}
```
    '''

    update.message.reply_text(msg, parse_mode=ParseMode.MARKDOWN)


def _format_departure(dep: dict) -> str:
    line = dep.get('line').ljust(5)
    direction = dep.get('direction').ljust(18)
    arrival = dep.get('arrival')

    if arrival == 0:
        arrival = ''

    return f'{line} {direction} {arrival}'


monitor_handler = CommandHandler('abfahrten', _monitor_cmd, pass_args=True)
monitor_shorthand_handler = CommandHandler('a', _monitor_cmd, pass_args=True)
