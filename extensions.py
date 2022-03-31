#Exceptions

class Error(Exception):
    """Base class for other exceptions"""
    pass


class APIException (Error):

    def __init__(self, bot, chat_id, text):
        bot.send_message(chat_id, text)
    pass

