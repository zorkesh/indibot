import requests
import config


item_types = {'head': 'Шлем', 'shoulder': 'Плечо', 'back': 'Плащ', 'neck': 'Шея', 'chest': 'Грудь', 'wrist': 'Наручи',
              'waist': 'Пояс', 'hands': 'Перчатки', 'shirt': 'Рубашка', 'legs': 'Штаны', 'feet': 'Боты',
              'finger1': 'Кольцо', 'finger2': 'Кольцо', 'trinket1': 'Аккс.', 'trinket2': 'Аккс.',
              'mainHand': 'Пр. рука', 'offHand': 'Лев. рука', 'tabard': 'Накидка'}


def get_char_items_info(char, realm):
    payload ={'locale': 'ru_RU', 'fields': 'items', 'apikey': config.bnet_token}
    res = requests.get(config.battle_net_url + '/character/' + realm + '/' + char, params=payload, verify=config.verification)
    character = res.json()
    return character


def parse_char_items(char):
    message = ''
    try:
        items = char['items']
        av_ilvl = items.pop('averageItemLevel')
        eq_ilvl = items.pop('averageItemLevelEquipped')
        message += '*Средний уровень предметов:* ' + str(av_ilvl) + '\n'
        message += '*Экипированный уровень предметов:* ' + str(eq_ilvl) + '\n'
        message += '*Предметы:*' + '\n'
        for i in items:
            item = items[i]
            message += u'\U000025CF' + '*' + item_types[i] + '*' + ': ' + item['name'] + '. ilvl: ' + \
                       str(item['itemLevel']) + '\n'
    except Exception:\
        message = 'Что-то не так. Гоблины украли персонажа?'
    return message