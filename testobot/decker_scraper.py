from urllib.request import urlopen
import re
from itertools import product
import requests


class Deck:
    def __init__(self, link):
        self.description = ''
        self.link = link
        self.ability = ''
        self.golden = ''
        self.faction = ''

    @property
    def smile(self):
        faction = self.faction
        if faction == "skellige":
            return '''🌊'''
        if faction == "monsters":
            return '''👹'''
        if faction == "nilfgaard":
            return '''🌞'''
        if faction == "scoiatael":
            return '''🐿'''
        if faction == "syndicate":
            return '''💰'''
        if faction == "northernrealms":
            return '''⚜️'''
        return faction

    @property
    def ru_faction(self):
        faction = self.faction
        if faction == "skellige":
            return 'Скеллиге'
        if faction == "monsters":
            return '''Чудовища'''
        if faction == "nilfgaard":
            return '''Нильфгаард'''
        if faction == "scoiatael":
            return '''Скоя'таэли'''
        if faction == "syndicate":
            return '''Синдикат'''
        if faction == "northernrealms":
            return '''Королевства Севера'''
        return faction


def get_youtube_name(url):
    with urlopen(url) as page:
        s = page.read().decode('utf-8').replace('&quot;', '"')
        nums = list(product('0123456789abcdef', repeat=4))
        nums = list(map(lambda x: ''.join(x), nums))
        d = {}
        for n in nums:
            d[n] = chr(int(n, base=16))
        s = re.sub('\\\\u[0-9a-f]{4}', lambda x: d[x.group()[2:]], s)
        s = s.replace('&#039;', "'")
    # return s
    # channel = re.findall('dialogMessages(.+)confirmButton', s)[0].split('text')[1]
    # channel = channel.replace('":"', '').replace('"},{"', '')
    name = re.findall('<title>(.+)</title>', s)[0]
    description = re.findall('shortDescription":"(.+)","isCrawlable', s)[0]
    return name, description


def get_links(description):
    result = []
    for d in description.split('\n'):
        result.extend(re.findall('playgwent.com/[a-z]+/decks/guides/\d+', d))
    return result


def get_image_link_and_name(url):
    with urlopen(url) as page:
        s = page.read().decode('utf-8').replace('&quot;', '"')
        nums = list(product('0123456789abcdef', repeat=4))
        nums = list(map(lambda x: ''.join(x), nums))
        d = {}
        for n in nums:
            d[n] = chr(int(n, base=16))
        s = re.sub('\\\\u[0-9a-f]{4}', lambda x: d[x.group()[2:]], s)
        s = s.replace('&#039;', "'")
    found = re.findall('assets_ability_icon(.+?(?=\.png))', s)
    ability_img = found[0]
    s1 = s.split('slotImgCn')[1]
    ability = get_tag(s1, 'localizedName')[0]
    link = 'https://www.playgwent.com/uploads/media/assets_ability_icon' + ability_img.replace('\\', '') + '.png'
    return link, ability


def download_picture(url):
    link, ability = get_image_link_and_name(url)
    response = requests.get(link)
    open(ability + '.png', "wb").write(response.content)


def get_tag(page, tag):
    return list(set(re.findall('"{0}":"?(.+?)(?=")'.format(tag), page)))


def get_real_tag(page, tag):
    return list(set(re.findall('<{0}>(.+)</{0}>'.format(tag), page)))


def where(dic, pred):
    ans = {}
    for key in dic:
        if pred(dic[key]):
            ans[key] = dic[key]
    return ans


def faction_w_smiles(faction):
    if faction == "skellige":
        return '''🌊''' + " Скеллиге"
    if faction == "monsters":
        return '''👹''' + " Чудовища"
    if faction == "nilfgaard":
        return '''🌞''' + " Нильфгаард"
    if faction == "scoiatael":
        return '''🐿''' + " Скоя'таэли"
    if faction == "syndicate":
        return '''💰''' + " Синдикат"
    if faction == "northernrealms":
        return '''⚜️''' + " Королевства Севера"
    return faction


def get_deck(url):
    if not url.startswith('https://'):
        url = 'https://' + url
    url = re.sub('.com/.+?(?=/)', '.com/ru', url)
    with urlopen(url) as page:
        s = page.read().decode('utf-8').replace('&quot;', '"')
        nums = list(product('0123456789abcdef', repeat=4))
        nums = list(map(lambda x: ''.join(x), nums))
        d = {}
        for n in nums:
            d[n] = chr(int(n, base=16))
        s = re.sub('\\\\u[0-9a-f]{4}', lambda x: d[x.group()[2:]], s)
        s = s.replace('&#039;', "'")
        s = s.split('slotImgCn')
        s1 = s[1]
        ability = get_tag(s1, 'localizedName')[0]
        faction = get_tag(s1, 'slug')[0]
        t = s[2:]
        cards = {}
        for c in t:
            try:
                name = get_tag(c, 'localizedName')[0]
                prov = get_tag(c, 'provisionsCost')[0].strip(',')
                rarity = get_tag(c, 'rarity')[0]
                # group = get_tag(c, 'cardGroup')[0]
                # card_faction = get_tag(c, 'slug')[0]
                cards[name] = rarity, prov # , group, card_faction
            except ReferenceError as e:
                print(e)
        cards.pop(ability)
        result = Deck(url)
        result.ability = ability
        result.faction = faction

        golden = where(cards, lambda card: card[0][0] in 'le')
        golden = list(dict(sorted(golden.items(), key=lambda x: int(x[1][1]), reverse=True)).keys())

        stratagem = list(where(cards, lambda x: x[1] == '0').keys())[0]
        golden.remove(stratagem)
        if stratagem not in ['Волшебная лампа', 'Тактическое преимущество']:
            golden.insert(0, stratagem)

        result.golden = ', '.join(golden)
        return result

deck = get_deck('https://www.playgwent.com/ru/decks/c92cc012d1bddbe8aa5d027d1ed3b3e8')