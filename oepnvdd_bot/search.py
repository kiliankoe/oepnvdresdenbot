import geopy.distance
from dvb import Stop, Departure
from telegram.ext import CommandHandler, MessageHandler, Filters, CallbackQueryHandler
from telegram.inline.inlinekeyboardbutton import InlineKeyboardButton
from telegram.inline.inlinekeyboardmarkup import InlineKeyboardMarkup
from telegram.parsemode import ParseMode

from .monitor import _format_departure

NEAREST_STOPS_COUNT = 5


def _search_cmd(bot, update, args):
    query = ' '.join(args)
    print(query)
    stop_res = Stop.find(query)

    if len(stop_res['stops']) == 0:
        update.message.reply_text('Keine Resultate gefunden.')
        return

    first_stop = stop_res['stops'][0]
    name = first_stop.name
    coords = (first_stop.latitude, first_stop.longitude)
    place = first_stop.place

    if place is not None:
        update.message.reply_text(f'Meintest du {name} in {place}?')
    else:
        update.message.reply_text(f'Meintest du {name}?')

    if len(coords) == 2:
        bot.send_location(chat_id=update.message.chat_id, latitude=coords[0], longitude=coords[1])


search_handler = CommandHandler('suche', _search_cmd, pass_args=True)
search_shorthand_handler = CommandHandler('s', _search_cmd, pass_args=True)


def _nearest_stops(bot, update):
    stop_res = Stop.find_near(update.message.location.latitude, update.message.location.longitude)

    user_pos = geopy.Point(update.message.location.latitude, update.message.location.longitude)

    if len(stop_res['stops']) == 0:
        update.message.reply_text('Keine Haltestellen im VVO Netz in deiner Umgebung gefunden.')
        return

    keyboard = []
    for stop in stop_res['stops'][:NEAREST_STOPS_COUNT]:
        stop_point = geopy.Point(stop.latitude, stop.longitude)
        distance = geopy.distance.distance(user_pos, stop_point).m
        keyboard.append([InlineKeyboardButton('{}, {} ({:.0f}m)'.format(stop.name, stop.place, distance),
                                              callback_data=stop.id)])

    reply_markup = InlineKeyboardMarkup(keyboard)

    bot.send_message(chat_id=update.message.chat_id,
                     text='Die {} nächsten Haltestellen in deiner Umgebung sind diese hier:'
                     .format(len(stop_res['stops'][:NEAREST_STOPS_COUNT])),
                     reply_markup=reply_markup)
    return


nearest_stops_handler = MessageHandler(Filters.location, _nearest_stops)


def _nearest_stops_callback(bot, update):
    stop_id = update.callback_query['data']

    departure_res = Departure.for_stop(stop_id)
    departures = departure_res['departures'][:10]

    if len(departures) == 0:
        bot.send_message(chat_id=update.callback_query.message.chat_id, text='Keine Abfahrten gefunden.')
        return

    joined_departures = '\n'.join([_format_departure(dep) for dep in departures])
    msg = f'''Abfahrten *{departure_res["name"]}*

```
{joined_departures}
```
        '''

    bot.send_message(chat_id=update.callback_query.message.chat_id,
                     text=msg,
                     parse_mode=ParseMode.MARKDOWN)


nearest_stops_callback_handler = CallbackQueryHandler(_nearest_stops_callback)
