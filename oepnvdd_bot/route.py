import dvb
from telegram.ext import CommandHandler


def _route_cmd(bot, update, args):
    pass


route_handler = CommandHandler('route', _route_cmd)
route_shorthand_handler = CommandHandler('r', _route_cmd)
