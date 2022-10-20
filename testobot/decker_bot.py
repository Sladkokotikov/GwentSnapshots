from telegram.ext import Updater, MessageHandler, Filters
from testobot import config
from testobot import user
from testobot import copypaster
from testobot.copypaster import command
from testobot import localization
from testobot.localization import Localization

print("Бот запущен. Нажмите Ctrl+C для завершения")

localizations = Localization(['ru', 'en'])

users = {}

updater = Updater(config.token, use_context=True)
dispatcher = updater.dispatcher


def text(username, tag):
    if username not in users:
        users[username] = user.User(username, 'ru')
    return localizations.languages[users[username].language][tag]


@command(dispatcher)
def make_snapshot(update, context):
    chat = update.effective_chat
    username = update.message.from_user.username
    if username not in users:
        users[username] = user.User(username, 'ru')

    if users[username].snapshot is not None:
        context.bot.send_message(chat_id=chat.id, text=text(username, 'snapshot_already_exists'))
        return

    users[username].intention = 'make_snapshot'
    context.bot.send_message(chat_id=config.log_chat_id, text=f'@{username} make_snapshot')
    context.bot.send_message(chat_id=chat.id, text=text(username, 'send_title'))


@command(dispatcher)
def preview(update, context):
    chat = update.effective_chat
    username = update.message.from_user.username
    if username not in users:
        users[username] = user.User(username, 'ru')

    if users[username].snapshot is None:
        context.bot.send_message(chat_id=chat.id, text=text(username, 'snapshot_dont_exist'))
        return
    context.bot.send_message(chat_id=config.log_chat_id, text=f'@{username} preview')
    context.bot.send_message(chat_id=chat.id, text=users[username].snapshot.to_stock(False), parse_mode="html")


@command(dispatcher)
def preview_stock(update, context):
    chat = update.effective_chat
    username = update.message.from_user.username
    if username not in users:
        users[username] = user.User(username, 'ru')

    if users[username].snapshot is None:
        context.bot.send_message(chat_id=chat.id, text=text(username, 'snapshot_dont_exist'))
        return
    context.bot.send_message(chat_id=config.log_chat_id, text=f'@{username} preview_stock')
    context.bot.send_message(chat_id=chat.id, text=users[username].snapshot.to_stock(True), parse_mode="html")


@command(dispatcher)
def preview_photo(update, context):
    chat = update.effective_chat
    username = update.message.from_user.username
    if username not in users:
        users[username] = user.User(username, 'ru')

    if users[username].snapshot is None:
        context.bot.send_message(chat_id=chat.id, text=text(username, 'snapshot_dont_exist'))
        return
    context.bot.send_message(chat_id=config.log_chat_id, text=f'@{username} preview_photo')
    context.bot.send_photo(chat_id=chat.id, photo=users[username].snapshot.to_image)


@command(dispatcher)
def sign(update, context):
    chat = update.effective_chat
    username = update.message.from_user.username
    if username not in users:
        users[username] = user.User(username, 'ru')
    if users[username].snapshot is None:
        context.bot.send_message(chat_id=chat.id, text=text(username, 'snapshot_dont_exist'))
        return
    users[username].snapshot.signed = True
    context.bot.send_message(chat_id=config.log_chat_id, text=f'@{username} sign')
    context.bot.send_message(chat_id=chat.id, text=text(username, 'signed_success'))


@command(dispatcher)
def unsign(update, context):
    chat = update.effective_chat
    username = update.message.from_user.username
    if username not in users:
        users[username] = user.User(username, 'ru')

    if users[username].snapshot is None:
        context.bot.send_message(chat_id=chat.id, text=text(username, 'snapshot_dont_exist'))
        return
    users[username].snapshot.signed = False
    context.bot.send_message(chat_id=config.log_chat_id, text=f'@{username} unsign')
    context.bot.send_message(chat_id=chat.id, text=text(username, 'unsigned_success'))


@command(dispatcher)
def discard(update, context):
    chat = update.effective_chat
    username = update.message.from_user.username
    if username not in users:
        users[username] = user.User(username, 'ru')

    if users[username].snapshot is None:
        context.bot.send_message(chat_id=chat.id, text=text(username, 'snapshot_dont_exist'))
        return
    users[username].snapshot = None
    context.bot.send_message(chat_id=config.log_chat_id, text=f'@{username} discard')
    context.bot.send_message(chat_id=chat.id, text=text(username, 'discarded_success'))


@command(dispatcher)
def publish(update, context):
    chat = update.effective_chat
    username = update.message.from_user.username
    if username not in users:
        users[username] = user.User(username, 'ru')

    if users[username].snapshot is None:
        context.bot.send_message(chat_id=chat.id, text=text(username, 'snapshot_dont_exist'))
        return
    context.bot.send_message(chat_id=config.log_chat_id, text=users[username].snapshot.to_stock(False), parse_mode="html")
    context.bot.send_message(chat_id=config.log_chat_id, text=users[username].snapshot.to_stock(True), parse_mode="html")
    context.bot.send_photo(chat_id=config.log_chat_id, photo=users[username].snapshot.to_image)

    context.bot.send_message(chat_id=chat.id, text=users[username].snapshot.to_stock(False), parse_mode="html")
    context.bot.send_message(chat_id=chat.id, text=users[username].snapshot.to_stock(True), parse_mode="html")
    context.bot.send_photo(chat_id=chat.id, photo=users[username].snapshot.to_image)

    users[username].snapshot = None
    context.bot.send_message(chat_id=config.log_chat_id, text=f'@{username} publish')
    context.bot.send_message(chat_id=chat.id, text=text(username, 'published_success'))


@command(dispatcher)
def usage_example(update, context):
    chat = update.effective_chat
    username = update.message.from_user.username
    context.bot.send_message(chat_id=chat.id, text="/make_snapshot")
    context.bot.send_message(chat_id=chat.id, text="Gwent in a nutshell")
    context.bot.send_message(chat_id=chat.id, text="/add_tier")
    context.bot.send_message(chat_id=chat.id, text="Start with S")
    context.bot.send_message(chat_id=chat.id, text="https://www.playgwent.com/ru/decks/guides/355955 Money on my mind")
    context.bot.send_message(chat_id=chat.id, text="https://www.playgwent.com/en/decks/guides/355919 Green bois")
    context.bot.send_message(chat_id=chat.id, text="https://www.playgwent.com/ru/decks/guides/355331 Hold my bear")
    context.bot.send_message(chat_id=chat.id, text="/add_tier")
    context.bot.send_message(chat_id=chat.id, text="We fight")
    context.bot.send_message(chat_id=chat.id, text="https://www.playgwent.com/en/decks/guides/355049 White moon")
    context.bot.send_message(chat_id=chat.id, text="https://www.playgwent.com/ru/decks/guides/356033 Shupe Soldja'")
    context.bot.send_message(chat_id=chat.id, text="/add_tier")
    context.bot.send_message(chat_id=chat.id, text="What am I doing here")
    context.bot.send_message(chat_id=chat.id, text="https://www.playgwent.com/en/decks/guides/355160 So cold!")
    context.bot.send_message(chat_id=chat.id, text="/unsign")
    context.bot.send_message(chat_id=chat.id, text="/publish")
    context.bot.send_message(chat_id=chat.id, text=text(username, "usage_script_end"))
    context.bot.send_message(chat_id=config.log_chat_id, text=f'@{username} usage_example')



@command(dispatcher)
def add_tier(update, context):
    chat = update.effective_chat
    username = update.message.from_user.username
    if username not in users:
        users[username] = user.User(username, 'ru')

    if users[username].snapshot is None:
        context.bot.send_message(chat_id=chat.id, text=text(username, 'snapshot_dont_exist'))
        return

    users[username].intention = 'add_tier'
    context.bot.send_message(chat_id=config.log_chat_id, text=f'@{username} add_tier')
    context.bot.send_message(chat_id=chat.id, text=text(username, 'send_tier_title'))


@command(dispatcher)
def start(update, context):
    chat = update.effective_chat
    username = update.message.from_user.username
    context.bot.send_message(chat_id=config.log_chat_id, text=f'@{username} start')
    context.bot.send_message(chat_id=chat.id, text=text(username, 'greetings'))


@command(dispatcher)
def help(update, context):
    chat = update.effective_chat
    username = update.message.from_user.username
    context.bot.send_message(chat_id=config.log_chat_id, text=f'@{username} help')
    context.bot.send_message(chat_id=chat.id, text=text(username, 'help'))


@command(dispatcher)
def future(update, context):
    username = update.message.from_user.username
    chat = update.effective_chat
    context.bot.send_message(chat_id=config.log_chat_id, text=f'@{username} future')
    context.bot.send_message(chat_id=chat.id, text=text(username, 'future'))


def lang_waiter(update, context):
    username = update.message.from_user.username
    if username not in users:
        users[username] = user.User(username, 'ru')
    users[username].language = update.message.text
    context.bot.send_message(chat_id=config.log_chat_id, text=f'@{username} lang {users[username].language}')
    context.bot.send_message(chat_id=update.effective_chat.id, text=text(username, 'lang_choice_success'))


def on_message(update, context):
    username = update.message.from_user.username
    chat = update.effective_chat
    if username not in users:
        users[username] = user.User(username, 'ru')
    result = users[username].process(update, context)
    for msg in result:
        context.bot.send_message(chat_id=config.log_chat_id, text=f'@{username} intention handled correctly')
        context.bot.send_message(chat_id=chat.id, text=text(username, msg))


dispatcher.add_handler(MessageHandler(Filters.text(list(localizations.languages.keys())), lang_waiter))
dispatcher.add_handler(MessageHandler(Filters.text, on_message))

updater.start_polling()
updater.idle()
