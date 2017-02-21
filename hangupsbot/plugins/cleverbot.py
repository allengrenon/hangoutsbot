# Set your API key by saying
# /bot config set cleverbot-api-key "EXAMPLE_API_KEY_REPLACE_THIS"
# to your bot

from cleverwrap import CleverWrap
from random import randrange, randint
import asyncio
import plugins
import logging

logger = logging.getLogger(__name__)
cw = None

def _initialise(bot):
    plugins.register_handler(_handle_incoming_message, type="message")
    plugins.register_user_command(["chat"])
    plugins.register_admin_command(["chatreset"])

@asyncio.coroutine
def _handle_incoming_message(bot, event, command):
    """Handle random message intercepting"""

    if not event.text:
        return

    if not bot.get_config_suboption(event.conv_id, 'cleverbot_percentage_replies'):
        return

    percentage = bot.get_config_suboption(event.conv_id, 'cleverbot_percentage_replies')

    if randrange(0, 101, 1) < float(percentage):
        yield from chat(bot, event)

def chat(bot, event, *args):
    """ Chat to Cleverbot. Usage: /bot chat hi cleverbot! """
    if not cw:
        api_key = bot.get_config_option("cleverbot_api_key")
        if not api_key:
            response = "API key not defined: config.cleverbot_api_key"
            logger.error(response)
            yield from bot.coro_send_message(event.conv_id, response)
            return
        else:
            global cw
            cw = CleverWrap(api_key)
    if args:
        input_text = " ".join(args)
    else:
        input_text = event.text
    response = cw.say(input_text)
    # cw.say takes one argument, the input string. It is a blocking call that returns cleverbot's response.
    # see https://github.com/edwardslabs/cleverwrap.py for more information
    yield from bot.coro_send_message(event.conv_id, response)


def chatreset(bot, event, *args):
    """Tell cleverbot to forget things you've said in the past"""
    if cw:
        cw.reset()
    yield from bot.coro_send_message(event.conv_id, "reset")
