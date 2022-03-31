import requests
import json
import telebot
import re
from config import *
from extensions import *

bot = telebot.TeleBot(TOKEN)


def get_rates(base_currency):
    # Извините, я сделал по-своему
    req = requests.get(f'https://api.currencyapi.com/v3/latest?apikey={API_KEY}&base_currency={base_currency}')
    json_data = json.loads(req.content)
    return json_data['data']


def get_quote(base, quote, amount):
    rates = get_rates(base)
    return "{:.2f}".format(float(rates[quote]['value']) * amount)


@bot.message_handler(commands=['start', 'help'])
def handle_start_help(message):
    bot.send_message(message.chat.id,
                     f"Привет, {message.chat.username}. Отправьте сообщение боту в виде /quote <имя валюты, цену которой "
                     f"хотите узнать> <имя валюты, в которой надо узнать цену первой валюты> <количество первой валюты>.\n"
                     f"Пример: /quote USD RUB 100\n"
                     f"Или наберите /values чтобы узнать список всех валют.")
    pass


@bot.message_handler(commands=['values'])
def handle_values(message):
    bot.send_message(message.chat.id, "Список доступных валют:")
    currency_list = ''
    for key in CURRENCIES:
        currency_list += f'{key} ({CURRENCIES[key]}) \n'
    bot.send_message(message.chat.id, currency_list)

    pass


@bot.message_handler(commands=['quote'])
def handle_quote(message):
    pattern = '^\s*/quote\s+([a-z]+)\s+([a-z]+)\s+([0-9]+\.*[0-9]*)\s*$'
    result = re.match(pattern, message.text, re.IGNORECASE)
    try:
        if not result:
            raise APIException(bot, message.chat.id, "Неверный формат ввода! Для помощи введите /help")
        else:
            currency_from = result.group(1).upper()
            currency_to = result.group(2).upper()
            currency_amount = float(result.group(3))
            if currency_from not in CURRENCIES.keys():
                raise APIException(bot, message.chat.id, f"Исходная валюта {currency_from} не поддерживается! /help")
            if currency_to not in CURRENCIES.keys():
                raise APIException(bot, message.chat.id, f"Целевая валюта {currency_to} не поддерживается! /help")
            if currency_amount <= 0:
                raise APIException(bot, message.chat.id, "Сумма должна быть больше нуля! /help")
            if currency_from == currency_to:
                raise APIException(bot, message.chat.id, "Валюты не должны совпадать! /help")

            try:
                the_quote = get_quote(currency_from, currency_to, currency_amount)
            except (requests.ConnectionError, requests.Timeout) as e:
                bot.send_message(message.chat.id, "Ошибка: не могу подключиться к API!")
            if the_quote:
                bot.send_message(message.chat.id, f"{the_quote} {currency_to}")
            else:
                raise APIException(bot, message.chat.id, "Что-то пошло не так")
    except APIException:
        pass
    pass


bot.polling(none_stop=True)
