import csv
import dvb
import geopy.distance
from telegram.ext import CommandHandler, MessageHandler, Filters
from telegram.keyboardbutton import KeyboardButton
from telegram.replykeyboardmarkup import ReplyKeyboardMarkup
from telegram.parsemode import ParseMode

NEAREST_STOPS_COUNT = 5


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


def _nearest_stops(bot, update):
    # thanks to @dirko for the original implementation of this!
    user_position = geopy.Point(update.message.location.latitude, update.message.location.longitude)

    with open('../all_stops.csv', 'r', encoding='utf-8') as file:
        csv_reader = csv.reader(file, delimiter=';')
        stops = []
        for row in csv_reader:
            name = f'{row[1]} {row[2]}'
            lat = float(row[3])
            lng = float(row[4])
            point = geopy.Point(lat, lng)
            distance = geopy.distance.distance(point, user_position).m
            stops.append((name, distance, (lat, lng)))

        nearest_stops = sorted(stops, key=lambda stop: stop[1])[:NEAREST_STOPS_COUNT]

        msg = 'Nächstgelegene Haltestellen:\n'
        for stop in nearest_stops:
            msg += f'\n- {stop[0]} [{stop[1]:.0f}m](https://google.de/maps?q={stop[2][0]},{stop[2][1]})'


        reply_keyboard = [[KeyboardButton(text=f'/a {n[0]}')] for n in nearest_stops]
        bot.sendMessage(chat_id=update.message.chat_id,
                        text=msg,
                        parse_mode=ParseMode.MARKDOWN,
                        reply_markup=ReplyKeyboardMarkup(reply_keyboard,
                                                         one_time_keyboard=True))


nearest_stations_handler = MessageHandler(Filters.location, _nearest_stops)
