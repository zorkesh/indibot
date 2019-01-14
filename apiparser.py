import json
from decimal import Decimal

import requests

import config
import tools
import indireq as irq

"""
Модуль для разбора данных ответа API Индикатора.
get* - получение JSON объекта из API
parse* - разбор JSON объекта и возврат текста для сообщения бота 
"""


def search(query):
    payload = {'query': query}
    headers = config.headers
    result = requests.get(irq.search, params=payload, headers=headers,
                          verify=config.verification)
    data = result.json()
    return data


def parse_search(data):
    if data:
        message = '*Результаты поиска (Топ-5)*\n'
        for i in range(5) if len(data) > 5 else range(len(data)):
            org_record = data['content'][i]['content']
            if 'kpp' in org_record:
                kpp = org_record['kpp']
            else:
                kpp = ''
            if 'name' in org_record:
                short_name = org_record['name']
            else:
                short_name = org_record['fullName']
            status = org_record['statusStr'].capitalize()
            inn = org_record['inn']
            message += short_name + "\n"
            message += "*Статус:* " + status + "\n"
            message += "*ИНН:* /" + inn + "\n"
            if not kpp == '':
                message += "*КПП:* " + kpp + "\n"
            if 'leader' in org_record:
                leader = org_record['leader']
                leader_position = '*' + leader['position'].capitalize() + '*'
                leader_name = leader['name']
                message += leader_position + ':' + leader_name + "\n"
            message += '*Адрес:*' + org_record['addressStr'] + '\n\n'
    else:
        message = "Ничего не найдено, уточните параметры поиска"
    return message


def get_main_info(inn):
    headers = config.headers
    result = requests.get(irq.company_card, headers=headers, verify=config.verification)
    if result.status_code:
        data = json.loads(result.text)['content']
    else:
        data = json.loads(result.text)
    return data
"""
deprecated
"""
"""
def getLeaders(inn):
    result = requests.get(irq., verify=config.verification)
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

"""

def getFinanceSummary(ogrn):
    result = requests.get(config.indicatorUrl + '/api/v1/entities/' + ogrn + '/legal_bookkeeping/summary', verify=config.verification)
    data = json.loads(result.text)
    if not data['content']['data']:
        data = json.loads(
            "{\"errorCode\":2000,\"inn\":\"25\",\"errorDescriptionRu\":\"Бухгалтерская отчетность не опубликована\","
            "\"errorDescriptionEn\":\"Contractor is not found\"}")
    return data


def get_rating(inn):
    headers = config.headers
    result = requests.get(irq.markers.format(inn), headers=headers, verify=config.verification)
    if result.status_code == 200:
        return json.loads(result.text)['content']
    else:
        return json.loads(result.text)


def parse_main_codes(org_card):
    ogrn = okpo = ''
    ogrn = org_card['ogrn']
    if 'okpo' in org_card:
        okpo = org_card['okpo']
    return ogrn, okpo


"""
TODO Переделать парс маркеров. Неудобный API
"""


def parse_rating(org_card):
    ratings = config.ratings
    numbers = config.numbers
    message = ''
    kpp = ''
    if 'kpp' in org_card:
        kpp = org_card['kpp']
    if 'shortName' in org_card:
        shortName = org_card['shortName']
    else:
        shortName = fullName = org_card['fullName']
    status = org_card['status'].capitalize()
    inn = org_card['inn']
    rInd = int(org_card['criticalFacts'])
    yInd = int(org_card['payAttentionFacts'])
    gInd = int(org_card['activityFacts'])
    bInd = int(org_card['achievements'])
    indicators = ratings['red'] + numbers[rInd] + ratings['yellow'] + numbers[yInd] + ratings['green'] + numbers[gInd] + ratings['blue'] + numbers[bInd]
    message += shortName + "\n\n"
    message += indicators + "\n\n"
    message += "*Статус:* " + status + "\n"
    message += "*ИНН:* " + inn + "\n"
    if not kpp == '':
        message += "*КПП:* " + kpp

    return message


def parse_org_card(org_card):
    rouble = config.rouble
    capital = ''
    main_activity = ''
    message = ''
    full_name = short_name = ''
    ogrn = org_card['ogrn']
    kpp = org_card['kpp']
    if 'shortName' in org_card:
        short_name = org_card['shortName']
    else:
        short_name = full_name = org_card['fullName']
    status = org_card['status']['name'].capitalize()
    inn = org_card['inn']
    if 'registrationDate' in org_card:
        reg_date = org_card['registrationDate']
    else:
        reg_date = org_card['ogrnAssignmentDate']
    address = ''
    if 'address' in org_card:
        if 'index' in org_card['address']:
            address += org_card['address']['index'] + ', '
        if 'region' in org_card['address']:
            if 'type' in org_card['address']['region']:
                address += org_card['address']['region']['type'].lower() + ' '
            if 'name' in org_card['address']['region']:
                address += org_card['address']['region']['name'].capitalize() + ', '
        if 'city' in org_card['address']:
            if 'type' in org_card['address']['city']:
                address += org_card['address']['city']['type'].lower() + ' '
            if 'name' in org_card['address']['city']:
                address += org_card['address']['city']['name'].capitalize() + ', '
        if 'street' in org_card['address']:
            if 'type' in org_card['address']['street']:
                address += org_card['address']['street']['type'].lower() + ' '
            if 'name' in org_card['address']['street']:
                address += org_card['address']['street']['name'].capitalize() + ', '
        if 'house' in org_card['address']:
            address += org_card['address']['house'].lower()
        if 'apartment' in org_card['address']:
            address += ', ' + org_card['address']['apartment'].lower()
    if 'authorizedCapital' in org_card:
        capital = tools.moneyfmt(Decimal(org_card['capitalValue']))
    if 'economicActivity' in org_card:
        main_activity = org_card['economicActivity']['main']['code'] + ' ' + org_card['economicActivity']['main']['name']
    message += short_name + "\n\n"
    message += "*Статус:* " + status + "\n"
    message += "*ИНН:* " + inn  + "\n"
    message += "*КПП:* " + kpp + "\n"
    message += "*ОГРН:* " + ogrn + "\n"
    message += "*Дата создания: *" + reg_date + "\n"
    message += "*Адрес:* " + address + "\n"
    if not capital == '':
        message += "*Уставный капитал: *" + capital + ' ' + rouble + "\n"
    message += "*Основной вид деятельности: *" + main_activity + "\n"
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
    rouble = config.rouble
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
    rouble = config.rouble
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
