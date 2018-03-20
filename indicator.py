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
                  "Поиск производится по ИНН, Наименованию, ФИО Руководителя, Учредителям, Адресу регистрации. \n" \
                  "Удачи "
    bot.send_message(message.chat.id, resultstart)


@bot.message_handler(regexp=r'\d{12}')
def handle_ip_message(message):
    try:
        inn = message.text.replace('/', '')
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
        inn = message.text.replace('/', '')
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
                finInfo = apiparser.getFinanceSummary(ogrn)
                respmessage += apiparser.parseFinSummary(finInfo) + "\n"
            bot.send_message(message.chat.id, respmessage, parse_mode='markdown')
        else:
            bot.send_message(message.chat.id, rate["errorDescriptionRu"])
    except Exception as e:
        bot.send_message(message.chat.id, 'Что-то пошло не так. Попробуйте позже\n' + str(e))


@bot.message_handler(func=lambda message: True, content_types=['text'])
def search_msg(message):
    # bot.send_message(message.chat.id, "Я пока не понимаю никаких сообщений кроме ИНН :(")
    # try:
    resp = apiparser.search(message.text)
    respmessage = apiparser.parseSearch(resp)
    bot.send_message(message.chat.id, respmessage, parse_mode='markdown')
    # except Exception as e:
    #     bot.send_message(message.chat.id, 'Что-то пошло не так. Попробуйте позже\n' + str(e))


@bot.inline_handler(func=lambda query: len(query.query) > 3)
def query_text(query):
    data = apiparser.search(query.query)
    if data:
        r_inf = []
        for i in range(5) if len(data) > 5 else range(len(data)):
            org = data[i]
            r_inf.append(types.InlineQueryResultArticle(id=i,
                                                        title=org['inn'],
                                                        description=org['name'] if 'name' in org else org['fullName'],
                                                        input_message_content=types.InputTextMessageContent(
                                                            message_text=org['inn'], parse_mode='markdown')))
        bot.answer_inline_query(query.id, r_inf)
    else:
        r_inf = types.InlineQueryResultArticle(id=1,
                                               title='',
                                               description="Ничего не найдено",
                                               input_message_content=types.InputTextMessageContent(message_text=inn,
                                                                                                   parse_mode='markdown'))
        bot.answer_inline_query(query.id, [r_inf])


if __name__ == '__main__':
    try:
        bot.polling(none_stop=True)
    except Exception as e:
        print(TypeError(e))
