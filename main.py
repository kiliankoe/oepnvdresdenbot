import os
import logging
import argparse

from telegram.ext import Updater

from oepnvdd_bot.monitor import *
from oepnvdd_bot.search import *
from oepnvdd_bot.route import *

parser = argparse.ArgumentParser()
parser.add_argument('--log', dest='loglevel', default='ERROR', help='log level')
args = parser.parse_args()

numeric_level = getattr(logging, args.loglevel.upper(), None)
if not isinstance(numeric_level, int):
    raise ValueError('Invalid log level: {}'.format(args.loglevel))
logging.basicConfig(level=numeric_level)


if __name__ == '__main__':
    updater = Updater(os.getenv('TELEGRAM_BOT_TOKEN'))
    dispatcher = updater.dispatcher

    dispatcher.add_handler(monitor_handler)
    dispatcher.add_handler(monitor_shorthand_handler)

    dispatcher.add_handler(search_handler)
    dispatcher.add_handler(search_shorthand_handler)
    dispatcher.add_handler(nearest_stops_handler)
    dispatcher.add_handler(nearest_stops_callback_handler)

    dispatcher.add_handler(route_handler)
    dispatcher.add_handler(route_shorthand_handler)

    updater.start_polling()
