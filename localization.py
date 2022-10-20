class Localization:

    def __init__(self, langs):
        self.languages = {}
        for lang in langs:
            self.add_language(lang)

    def add_language(self, lang):
        self.languages[lang] = {}
        with open(f'testobot/localizations/{lang}.txt', encoding='utf-8') as file:
            s = file.read().strip().split(';')
            for line in s:
                name, text = line.strip().split('=', 1)
                self.languages[lang][name] = text
