# -*- coding: utf-8 -*-
import json

import config
import telebot
import bnet
from telebot import types


bot = telebot.TeleBot(config.token)


@bot.message_handler(commands=['start', 'help'])
def handle_start_help(message):
    result_start = "Здравствуйте. \n" \
             "Введите команду /char и имя персонажа для поиска и анализа \n" \
                   "Например /char Золтарн Вечная Песня"
    bot.send_message(message.chat.id, result_start)


@bot.message_handler(commands=['char'])
def handle_char_message(message):
    try:
        command, char, *realm = map(str, message.text.split())
        character = bnet.get_char_items_info(char, ' '.join(realm))
        result = bnet.parse_char_items(character)
    except Exception:
        result = 'Что-то не так. Опять гоблины шалят?'
    bot.send_message(message.chat.id, result, parse_mode='markdown')


if __name__ == '__main__':
    try:
        bot.polling(none_stop=True)
    except Exception as e:
        print(TypeError(e))
