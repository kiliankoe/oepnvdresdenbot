import dvb
from telegram.ext import CommandHandler


def _route_cmd(bot, update, args):
    update.message.reply_text('Dieser Befehl funktioniert leider aktuell nicht. '
                              'Probiere es doch bitte demnächst wieder.')
    return


route_handler = CommandHandler('route', _route_cmd)
route_shorthand_handler = CommandHandler('r', _route_cmd)
