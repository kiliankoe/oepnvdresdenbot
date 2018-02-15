import os

from telegram.ext import Updater

from oepnvdd_bot.monitor import *
from oepnvdd_bot.search import *


if __name__ == '__main__':
    updater = Updater(os.getenv('TELEGRAM_BOT_TOKEN'))
    dispatcher = updater.dispatcher

    dispatcher.add_handler(monitor_handler)
    dispatcher.add_handler(monitor_shorthand_handler)

    dispatcher.add_handler(search_handler)
    dispatcher.add_handler(search_shorthand_handler)

    updater.start_polling()
