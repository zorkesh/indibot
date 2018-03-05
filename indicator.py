# -*- coding: utf-8 -*-
import json

import config
import telebot
import os
import requests


bot = telebot.TeleBot(config.token)
os.environ["HTTPS_PROXY"] = 'https://istomin:zer4ty5@proxy.bifit.int:3128'
os.environ["HTTP_PROXY"] = 'http://istomin:zer4ty5@proxy.bifit.int:3128'


def parseOrgrecord(orgRecord):
    fullName = shortName = ''
    ogrn = orgRecord['ogrn']
    if 'fullName' in orgRecord:
        fullName = orgRecord['fullName']
    if 'shortName' in orgRecord:
        shortName = orgRecord['shortName']
    status = orgRecord['status']['statusName']
    inn = orgRecord['inn']
    address = ''
    region = ''
    if 'address' in orgRecord:
        if 'index' in orgRecord['address']:
            address += orgRecord['address']['index'] + ', '
        if 'region' in orgRecord['address']:
            if 'name' in orgRecord['address']['region']:
                region += orgRecord['address']['region']['name'] + ' '
            if 'type' in orgRecord['address']['region']:
                region += orgRecord['address']['region']['type'] + ', '
        if 'city' in orgRecord['address']:
            if 'type' in orgRecord['address']['city']:
                address += orgRecord['address']['city']['type'] + ' '
            if 'name' in orgRecord['address']['city']:
                address += orgRecord['address']['city']['name'] + ', '
        if 'street' in orgRecord['address']:
            if 'type' in orgRecord['address']['street']:
                address += orgRecord['address']['street']['type'] + ' '
            if 'name' in orgRecord['address']['street']:
                address += orgRecord['address']['street']['name'] + ', '
        if 'house' in orgRecord['address']:
            address += orgRecord['address']['house']
        if 'apartment' in orgRecord['address']:
            address += ', ' + orgRecord['address']['apartment']
    return "ОГРН: " + ogrn + "\n" + "ИНН: " + inn + "\n" + "Краткое наименование: " + shortName + "\n" + \
          "Полное наименование: " + fullName + "\n" + "Адрес: " + address + "\n" + "Статус: " + status



@bot.message_handler(regexp=r'\d{10}')
def handle_message(message):
    payload = {'inn': message.text, 'installation_id': 9999}
    rorg = requests.get(config.indicatorUrl + '/api/v0/orginfo/organizations/record', params=payload, verify=False)
    if rorg.text:
        orginforecord = json.loads(rorg.text)
    else:
        orginforecord = json.loads(
            "{\"errorCode\":2000,\"inn\":\"25\",\"errorDescriptionRu\":\"Контрагент не найден\","
            "\"errorDescriptionEn\":\"Contractor is not found\"}")
    if not 'errorDescriptionRu' in orginforecord:
        bot.send_message(message.chat.id, parseOrgrecord(orginforecord))
    else:
        bot.send_message(message.chat.id, orginforecord["errorDescriptionRu"])


if __name__ == '__main__':
    bot.polling(none_stop=True)
