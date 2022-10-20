from testobot import tiermaking


class User:
    def __init__(self, username, language):
        self.username = username
        self.language = language
        self.snapshot = None
        self.intention = ''

        self.actions = {
            'make_snapshot': self.make_snapshot,
            'add_tier': self.add_tier,
            'add_deck': self.add_deck
        }

    def make_snapshot(self, update, context):
        message = update.message.text
        self.snapshot = tiermaking.Snapshot(message, self.username)
        self.intention = ''
        return ['snapshot_title_set', 'can_send_tiers']

    def add_tier(self, update, context):
        message = update.message.text
        self.snapshot.tiers[message] = tiermaking.Tier(message)
        self.snapshot.current_tier = message
        self.intention = 'add_deck'
        return ['tier_title_set', 'can_send_decks']

    def add_deck(self, update, context):
        message = update.message.text
        link, description = message.split(' ', 1)
        self.snapshot.tiers[self.snapshot.current_tier].add_deck(link, description)
        self.intention = 'add_deck'
        return ['deck_added']

    def process(self, update, context):
        if self.intention not in self.actions:
            return ['no_answer_needed']
        return self.actions[self.intention](update, context)
