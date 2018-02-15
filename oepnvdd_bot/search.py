import dvb
from telegram.ext import CommandHandler


def _search_cmd(bot, update, args):
    query = ' '.join(args)
    results = dvb.find(query)

    if len(results) == 0:
        update.message.reply_text('Keine Resultate gefunden.')
        return

    first = results[0]
    name = first.get('name')
    coords = first.get('coords')
    city = first.get('city')

    if city is not None:
        update.message.reply_text(f'Meintest du {name} in {city}?')
    else:
        update.message.reply_text(f'Meintest du {name}?')

    if len(coords) == 2:
        bot.send_location(latitude=coords[0], longitude=coords[1])


search_handler = CommandHandler('suche', _search_cmd, pass_args=True)
search_shorthand_handler = CommandHandler('s', _search_cmd, pass_args=True)
