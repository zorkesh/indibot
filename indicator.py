# -*- coding: utf-8 -*-
import json

import re

import apiparser
import config
import telebot
from telebot import types
import os
import requests


bot = telebot.TeleBot(config.token)


@bot.message_handler(commands=['start', 'help'])
def handle_start_help(message):
    resultstart = "Здравствуйте. \n" \
             "Я бот для получения информации о юридических лицах " \
                  "и индивидуальных предпринимателях из сервиса \"Индикатор\"\n" \
             "Пока только о юридических лицах =)\n" \
             "Для поиска введите 10 значный ИНН \n" \
                  "Удачи "
    bot.send_message(message.chat.id, resultstart)


@bot.message_handler(regexp=r'\d{12}')
def handle_ip_message(message):
    try:
        inn = message.text
        rate = apiparser.getRating(inn)
        if not 'errorDescriptionRu' in rate:
            respmessage = ''
            ratemessage = apiparser.parseRating(rate)
            respmessage += ratemessage + "\n"
            orginforecord = apiparser.getMainInfo(inn)
            # Ищем организацию
            mainInfo = apiparser.parseOrgrecord(orginforecord)
            respmessage += mainInfo + "\n"
            bot.send_message(message.chat.id, respmessage, parse_mode='markdown')
        else:
            bot.send_message(message.chat.id, rate["errorDescriptionRu"])
    except Exception as e:
        bot.send_message(message.chat.id, 'Что-то пошло не так. Попробуйте позже\n' + str(e))


@bot.message_handler(regexp=r'\d{10}')
def handle_message(message):
    try:
        inn = message.text
        rate = apiparser.getRating(inn)
        if not 'errorDescriptionRu' in rate:
            respmessage = ''
            ratemessage = apiparser.parseRating(rate)
            respmessage += ratemessage + "\n"
            orginforecord = apiparser.getMainInfo(inn)
            ogrn, okpo = apiparser.parsemaincodes(orginforecord)
            # Ищем организацию
            mainInfo = apiparser.parseOrgrecord(orginforecord)
            respmessage += mainInfo + "\n"
            # Ищем директоров
            leadersInfo = apiparser.getLeaders(inn)
            respmessage += apiparser.parseLeaders(leadersInfo) + "\n"
            # TODO Добавить учредителей
            foundersInfo = apiparser.getFounders(ogrn)
            respmessage += apiparser.parseFounders(foundersInfo) + "\n"
            # Ищем бух.отчетнсть
            if okpo == '':
                respmessage += "*Бухгалтерская отчетность не опубликована*"
            else:
                finInfo = apiparser.getFinanceSummary(okpo)
                respmessage += apiparser.parseFinSummary(finInfo) + "\n"
            bot.send_message(message.chat.id, respmessage, parse_mode='markdown')
        else:
            bot.send_message(message.chat.id, rate["errorDescriptionRu"])
    except Exception as e:
        bot.send_message(message.chat.id, 'Что-то пошло не так. Попробуйте позже\n')


@bot.message_handler(func=lambda message: True, content_types=['text'])
def echo_msg(message):
    bot.send_message(message.chat.id, "Я пока не понимаю никаких сообщений кроме ИНН :(")


@bot.inline_handler(func=lambda query: len(query.query) > 0)
def query_text(query):
    pattern = re.compile(r'\d{10}', re.MULTILINE)
    try:
        matches = re.match(pattern, query.query)
        if not matches:
            return
    # Вылавливаем ошибку, если вдруг юзер ввёл чушь
    # или задумался после ввода первого числа
    except AttributeError:
        return
    inn = matches.string
    org = apiparser.getRating(inn)
    if not 'errorDescriptionRu' in org:
        r_inf = types.InlineQueryResultArticle(id=1,
                                               title=inn,
                                               description=org['shortName'] if 'shortName' in org else org['fullName'],
                                               input_message_content=types.InputTextMessageContent(message_text=inn,
                                                                                                   parse_mode='markdown'))
        bot.answer_inline_query(query.id, [r_inf])
    else:
        r_inf = types.InlineQueryResultArticle(id=1,
                                               title=inn,
                                               description="Контрагент не найден",
                                               input_message_content=types.InputTextMessageContent(message_text=inn,
                                                                                                   parse_mode='markdown'))
        bot.answer_inline_query(query.id, [r_inf])


if __name__ == '__main__':
    bot.polling(none_stop=True)
