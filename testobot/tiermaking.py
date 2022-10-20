from PIL import Image, ImageFont, ImageDraw
from testobot import decker_scraper as ds
from testobot import config


def get_size(font, text):
    x0, y0, x1, y1 = font.getbbox(text)
    return x1 - x0, y1 - y0


def optimal_split(columns, tiers):
    if columns == 2:
        a, b = tiers[0], sum(tiers[1:])
        min_delta = abs(b - a)
        edge = 0
        for i in range(1, len(tiers)):
            a += tiers[i]
            b -= tiers[i]
            delta = abs(b - a)
            if delta < min_delta:
                min_delta = delta
                edge = i
        return [tiers[:edge+1], tiers[edge+1:]]
    if columns == 1:
        return [tiers]


def scale_font(text, default_size, expected_size):
    font = ImageFont.truetype(config.font, default_size)

    exp_w, exp_h = expected_size
    width = get_size(font, text)[0]

    while width > exp_w:
        font = ImageFont.truetype(config.font, int(font.size / width * exp_w))
        width = get_size(font, text)[0]

    height = get_size(font, text)[1]
    while height > exp_h:
        font = ImageFont.truetype(config.font, int(font.size / height * exp_h))
        height = get_size(font, text)[1]
    return font


class Tier:
    def __init__(self, name):
        self.name = name
        self.decks = []

    def add_deck(self, link, description):
        deck = ds.get_deck(link)
        deck.description = description
        self.decks.append(deck)


class Snapshot:
    def __init__(self, author, occupant):
        self.author = author
        self.tiers = dict()
        self.occupant = occupant
        self.current_tier = ''
        self.signed = True

    def load(self, info):
        info = info.split('\n')
        for tier in info:
            # Тир 1: https://playgwent.com/decks/guides/99999(Trolling)
            tier_name, decks = tier.split(':', 1)
            tier_name = tier_name.strip()
            decks = decks.strip().split(',')
            self.tiers[tier_name] = Tier(tier_name)
            for link in decks:
                link = link.strip()
                try:
                    if '(' in link:
                        deck = ds.get_deck(link.split('(')[0])
                        deck.description = link.split('(')[1][:-1]
                    else:
                        deck = ds.get_deck(link)
                        deck.description = deck.ability
                    self.tiers[tier_name].decks.append(deck)
                except UnicodeEncodeError:
                    pass

    @property
    def decks_count(self):
        return sum([len(v.decks) for v in self.tiers.values()])

    @property
    def to_image(self):
        img = Image.open(config.background_path)
        img_w, img_h = img.width, img.height
        draw = ImageDraw.Draw(img)
        author_font = scale_font(self.author, config.default_author_font_size,
                                 (img_w - 2 * config.side_author, config.author_h))
        draw.text((img_w // 2, config.up_author),
                  self.author,
                  (255, 255, 255),
                  font=author_font,
                  anchor='mt',
                  stroke_width=2,
                  stroke_fill=(0, 0, 0))

        count = self.decks_count
        columns = 2 if count > config.max_decks_in_column else 1
        optimal = optimal_split(columns, [len(t.decks) for t in self.tiers.values()])
        print(optimal)
        tier_count = 0
        tiers_list = list(self.tiers.values())

        max_cursor_y = 0

        for i in range(len(optimal)):
            cursor_y = config.up_author + config.author_h + config.author_tier
            cursor_x = img_w // 2 - config.tier_tier // 2 - config.deck_w[columns] // (3 - columns) + (
                    config.tier_tier + config.deck_w[columns]) * i
            for _ in range(len(optimal[i])):
                tier = tiers_list[tier_count]
                tier_font = scale_font(tier.name, config.default_tier_font_size,
                                       (config.tier_w[columns], config.tier_h))
                tier_w = get_size(tier_font, tier.name)[0]
                cursor_x += config.tier_w[columns] // 2 - tier_w // 2
                draw.text((cursor_x, cursor_y),
                          tier.name,
                          (255, 255, 255),
                          font=tier_font,
                          stroke_width=2,
                          stroke_fill=(0, 0, 0))
                cursor_x -= (config.tier_w[columns] // 2 - tier_w // 2)
                cursor_y += config.tier_h + config.tier_decks
                for deck in tier.decks:
                    faction_back = Image.open('testobot/backgrounds/' + deck.faction + '.jpg')
                    faction_back = faction_back.resize((config.deck_w[columns],
                                                        int(faction_back.height / faction_back.width * config.deck_w[
                                                            columns])))
                    faction_back = faction_back.crop((0, 0, config.deck_w[columns], config.deck_h))
                    img.paste(faction_back, (cursor_x, cursor_y))

                    ability_img = Image.open('testobot/abilities/' + deck.ability + '.png').resize(
                        (config.ability_w, config.ability_w))
                    img.paste(ability_img, (cursor_x - config.ability_w // 2, cursor_y), ability_img)
                    deck_font = scale_font(deck.description,
                                           config.default_deck_font_size,
                                           (config.deck_w[
                                                columns] - 2 * config.deck_description_margin - config.ability_w // 2,
                                            config.deck_h - 2 * config.deck_description_margin))

                    d_h = get_size(deck_font, deck.description)[1]

                    draw.text((cursor_x + config.ability_w // 2 + config.deck_description_margin,
                               cursor_y + config.deck_h // 2 - d_h // 2),
                              deck.description,
                              (255, 255, 255),
                              font=deck_font,
                              stroke_width=2,
                              stroke_fill=(0, 0, 0))
                    cursor_y += config.deck_deck + config.deck_h
                cursor_y -= config.deck_deck
                cursor_y += config.deck_tier
                max_cursor_y = max(max_cursor_y, cursor_y)
                tier_count += 1
        h = 0
        if self.signed:
            composer_name = 'Составил @' + self.occupant
            composer_font = scale_font(composer_name, config.composer_default_font_size,
                                       (config.composer_w, config.composer_h))
            h = get_size(composer_font, composer_name)[1]
            draw.text((img_w // 2, max_cursor_y),
                      composer_name,
                      (255, 255, 255),
                      font=composer_font,
                      anchor='mt',
                      stroke_width=2,
                      stroke_fill=(0, 0, 0))
        img = img.crop((0, 0, img_w, max_cursor_y + h + config.down_composer))
        path = 'testobot/snapshots/' + self.author + '.png'
        img.save(path)
        return open(path, 'rb')

    @property
    def preview(self):
        result = ''
        result += self.author + '\n'
        for k in self.tiers:
            result += k + '\n'
            for deck in self.tiers[k].decks:
                result += '    {0} {1}'.format(deck.ability, deck.description) + '\n'
        if self.signed:
            result += f'made by @{self.occupant}'
        return result

    def to_stock(self, full):
        result = f'<b>{self.author}</b>\n\n'
        # text='<a href="{0}">{1}</a>'.format(text, golds)
        for k in self.tiers:
            result += f'<b>{k}</b>\n'
            for deck in self.tiers[k].decks:
                deck_link = '<a href="{0}">{1}</a>'.format(deck.link, deck.description if not full else deck.golden)
                result += '{0} {1} - {2} {3}'.format(deck.smile,
                                                     deck.ru_faction,
                                                     deck.ability,
                                                     deck_link) + '\n'
        if self.signed:
            result += f'made by @{self.occupant}'
        return result
