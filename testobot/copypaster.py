from telegram.ext import CommandHandler


def command(dispatcher):
    def _wrapper(func):
        dispatcher.add_handler(CommandHandler(func.__name__, func))

        def __wrapper(*args, **kwargs):
            func(*args, **kwargs)

        return __wrapper

    return _wrapper


def keywords(keywords_list):
    def _wrapper(func):
        def __wrapper(update, context):
            text = update.message.text
            print(text)
            print(keywords_list)
            if text not in keywords_list:
                return
            func(update, context)

        return __wrapper

    return _wrapper
