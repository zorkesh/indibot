import json
from decimal import Decimal

import requests

import config
import tools
"""
Модуль для разбора данных ответа API Индикатора.
get* - получение JSON объекта из API
parse* - разбор JSON объекта и возврат текста для сообщения бота 
"""

ratings = {'green': u'\U0001F4D7', 'red': u'\U0001F4D5', 'blue': u'\U0001F4D8', 'yellow': u'\U0001F4D9'}
numbers = [u'\U00000030'+u'\U000020E3', u'\U00000031'+u'\U000020E3', u'\U00000032'+u'\U000020E3',
           u'\U00000033'+u'\U000020E3', u'\U00000034'+u'\U000020E3', u'\U00000035'+u'\U000020E3',
           u'\U00000036'+u'\U000020E3', u'\U00000037'+u'\U000020E3', u'\U00000038'+u'\U000020E3',
           u'\U00000039'+u'\U000020E3']
rouble = u'\U000020BD'


def search(query):
    payload = {'query': query, 'installationId': 9999, 'clientGuid': 'E2379CB15C9F4B54A77DBBF1CC6EC91C'}
    headers = {"Content-Type": "application/json"}
    result = requests.get(config.indicatorUrl + '/search', params=payload, headers=headers, verify=config.verification)
    data = result.json()['data']
    return data


def parseSearch(data):
    if data:
        message = '*Результаты поиска (Топ-5)*\n'
        for i in range(5) if len(data) > 5 else range(len(data)):
            orgRecord = data[i]
            if 'kpp' in orgRecord:
                kpp = orgRecord['kpp']
            else:
                kpp = ''
            if 'name' in orgRecord:
                shortName = orgRecord['name']
            else:
                shortName = orgRecord['fullName']
            status = orgRecord['status'].capitalize()
            inn = orgRecord['inn']
            message += shortName + "\n"
            message += "*Статус:* " + status + "\n"
            message += "*ИНН:* /" + inn + "\n"
            if not kpp == '':
                message += "*КПП:* " + kpp + "\n"
            if 'leader' in orgRecord:
                leader = orgRecord['leader']
                leaderPosition = '*' + orgRecord['leaderPosition'].capitalize() + '*'
                message += leaderPosition + ':' + leader + "\n"
            message += '*Адрес:*' + orgRecord['address'] + '\n\n'
    else:
        message = "Ничего не найдено, уточните параметры поиска"
    return message


def getMainInfo(inn):
    payload = {'inn': inn, 'installation_id': 9999}
    result = requests.get(config.indicatorUrl + '/api/v0/orginfo/organizations/record', params=payload, verify=config.verification)
    if result.text:
        data = json.loads(result.text)
    else:
        data = json.loads(
            "{\"errorCode\":2000,\"inn\":\"25\",\"errorDescriptionRu\":\"Контрагент не найден\","
            "\"errorDescriptionEn\":\"Contractor is not found\"}")
    return data


def getLeaders(inn):
    payload = {'inn': inn, 'installation_id': 9999}
    result = requests.get(config.indicatorUrl + '/api/v0/orginfo/leaders/list', params=payload, verify=config.verification)
    if result.text:
        data = json.loads(result.text)
    else:
        data = json.loads(
            "{\"errorCode\":2000,\"inn\":\"25\",\"errorDescriptionRu\":\"Информации о лидерах нет\","
            "\"errorDescriptionEn\":\"Contractor is not found\"}")
    return data


def getFounders(ogrn):
    payload = {'inn': ogrn, 'installation_id': 9999}
    result = requests.get(config.indicatorUrl + '/api/v1/entities/' + ogrn + '/stakes', params=payload, verify=config.verification)
    data = json.loads(result.text)
    if not data['content']:
        data = json.loads(
            "{\"errorCode\":2000,\"inn\":\"25\",\"errorDescriptionRu\":\"Информации об учредителях нет\","
            "\"errorDescriptionEn\":\"Contractor is not found\"}")
    return data


def getFinanceSummary(ogrn):
    result = requests.get(config.indicatorUrl + '/api/v1/entities/' + ogrn + '/legal_bookkeeping/summary', verify=config.verification)
    data = json.loads(result.text)
    if not data['content']['data']:
        data = json.loads(
            "{\"errorCode\":2000,\"inn\":\"25\",\"errorDescriptionRu\":\"Бухгалтерская отчетность не опубликована\","
            "\"errorDescriptionEn\":\"Contractor is not found\"}")
    return data


def getRating(inn):
    payload = {'inn': inn, 'installation_id': 9999}
    result = requests.get(config.indicatorUrl + '/rating', params=payload, verify=config.verification)
    return json.loads(result.text)


def parsemaincodes(orgRecord):
    ogrn = okpo = ''
    ogrn = orgRecord['ogrn']
    if 'okpo' in orgRecord:
        okpo = orgRecord['okpo']
    return ogrn, okpo


def parseRating(orgRecord):
    message = 'Краткая информация о '
    kpp = ''
    if 'kpp' in orgRecord:
        kpp = orgRecord['kpp']
    if 'shortName' in orgRecord:
        shortName = orgRecord['shortName']
    else:
        shortName = fullName = orgRecord['fullName']
    status = orgRecord['status'].capitalize()
    inn = orgRecord['inn']
    rInd = int(orgRecord['criticalFacts'])
    yInd = int(orgRecord['payAttentionFacts'])
    gInd = int(orgRecord['activityFacts'])
    bInd = int(orgRecord['achievements'])
    indicators = ratings['red'] + numbers[rInd] + ratings['yellow'] + numbers[yInd] + ratings['green'] + numbers[gInd] + ratings['blue'] + numbers[bInd]
    message += shortName + "\n\n"
    message += indicators + "\n\n"
    message += "*Статус:* " + status + "\n"
    message += "*ИНН:* " + inn + "\n"
    if not kpp == '':
        message += "*КПП:* " + kpp

    return message


def parseOrgrecord(orgRecord):
    capital = ''
    mainActivity = ''
    message = ''
    fullName = shortName = ''
    ogrn = orgRecord['ogrn']
    # if 'fullName' in orgRecord:
    #     fullName = orgRecord['fullName']
    if 'shortName' in orgRecord:
        shortName = orgRecord['shortName']
    else:
        shortName = fullName = orgRecord['fullName']
    status = orgRecord['status']['statusName'].capitalize()
    inn = orgRecord['inn']
    if 'registrationDate' in orgRecord:
        regdate = orgRecord['registrationDate']
    else:
        regdate = orgRecord['ogrnDate']
    address = ''
    if 'address' in orgRecord:
        if 'index' in orgRecord['address']:
            address += orgRecord['address']['index'] + ', '
        if 'region' in orgRecord['address']:
            if 'type' in orgRecord['address']['region']:
                address += orgRecord['address']['region']['type'].lower() + ' '
            if 'name' in orgRecord['address']['region']:
                address += orgRecord['address']['region']['name'].capitalize() + ', '
        if 'city' in orgRecord['address']:
            if 'type' in orgRecord['address']['city']:
                address += orgRecord['address']['city']['type'].lower() + ' '
            if 'name' in orgRecord['address']['city']:
                address += orgRecord['address']['city']['name'].capitalize() + ', '
        if 'street' in orgRecord['address']:
            if 'type' in orgRecord['address']['street']:
                address += orgRecord['address']['street']['type'].lower() + ' '
            if 'name' in orgRecord['address']['street']:
                address += orgRecord['address']['street']['name'].capitalize() + ', '
        if 'house' in orgRecord['address']:
            address += orgRecord['address']['house'].lower()
        if 'apartment' in orgRecord['address']:
            address += ', ' + orgRecord['address']['apartment'].lower()
    if 'capitalValue' in orgRecord:
        capital = tools.moneyfmt(Decimal(orgRecord['capitalValue']))
    if 'mainEconomicActivity' in orgRecord:
        mainActivity = orgRecord['mainEconomicActivity']['code'] + ' ' + orgRecord['mainEconomicActivity']['name']

    message += "*ОГРН:* " + ogrn + "\n"
    message += "*Дата создания: *" + regdate + "\n"
    message += "*Адрес:* " + address + "\n"
    if not capital == '':
        message += "*Уставный капитал: *" + capital + ' ' + rouble + "\n"
    message += "*Основной вид деятельности: *" + mainActivity + "\n"
    return message


def parseLeaders(orgRecord):
    message = ''
    if not 'errorDescriptionRu' in orgRecord:
        for auth_data in orgRecord:
            if 'patronymic' in auth_data:
                patr = auth_data['patronymic']
            else:
                patr = ''
            fio = auth_data['surname'].capitalize() + ' ' + auth_data['firstName'].capitalize() + ' ' + patr.capitalize()
            # fio = re.sub(u'[Ёё]', u'Е', fio)
            position = auth_data['position']
            message += '*' + position.capitalize() + ':* '
            message += fio + "\n"
    else:
        message = orgRecord['errorDescriptionRu']
    return message


def parseFounders(orgRecord):
    message = '*Учредители: *\n'
    if not 'errorDescriptionRu' in orgRecord:
        for founder_data in orgRecord['content']:
            if not founder_data['content']['stakeOwner']['type'] == 'PERSON':
                name = founder_data['content']['stakeOwner']['fullName']
            else:
                if 'patronymic' in founder_data['content']['stakeOwner']:
                    patr = founder_data['content']['stakeOwner']['patronymic']
                else:
                    patr = ''
                name = founder_data['content']['stakeOwner']['surname'].capitalize() + ' ' + \
                       founder_data['content']['stakeOwner']['name'].capitalize() + ' ' + patr.capitalize()
            if 'inn' in founder_data['content']['stakeOwner']:
                inn = founder_data['content']['stakeOwner']['inn']
            else:
                inn = ''
            stake = founder_data['content']['stakeSize']
            try:
                stake_size = tools.moneyfmt(Decimal(stake)) + ' ' + rouble
            except Exception:
                stake_size = str(stake)
            message += u'\U000025CF' + str(name) + ' - ' + stake_size + '\n'
            if not inn == '':
                message += '(ИНН: ' + inn + ')' + '\n'
    else:
        message = orgRecord['errorDescriptionRu'] + '\n'
    return message


def parseFinSummary(orgRecord):
    message = '*Бухгалтерская отчетность за '
    if not 'errorDescriptionRu' in orgRecord:
        year = sorted(list(orgRecord['content']['data'].keys()))[-1]
        message += year + " год.*" + "\n"
        lastdata = orgRecord['content']['data'][year]
        message += "*Баланс: *" + tools.moneyfmt(Decimal(lastdata['actives'])) + ' ' + rouble + '\n'
        message += "*Выручка: *" + tools.moneyfmt(Decimal(lastdata['earnings'])) + ' ' + rouble + '\n'
        if Decimal(lastdata['profit']) >= 0:
            message += "*Прибыль: *" + tools.moneyfmt(Decimal(lastdata['profit'])) + ' ' + rouble + '\n'
        else:
            message += "*Убыток: *" + tools.moneyfmt(Decimal(lastdata['profit']), neg='') + ' ' + rouble + '\n'
    else:
        message = "*" + orgRecord['errorDescriptionRu'] + "*"
    return message
