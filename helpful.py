def authorize(update, context, snapshot):
    chat = update.effective_chat
    username = update.message.from_user.username
    if snapshot.occupant != username:
        context.bot.send_message(chat_id=chat.id, text="This snapshot is edited right now. Please contact @" + snapshot.occupant)
        return None, None
    return chat, username


def occupy(update, context, snapshot):
    chat = update.effective_chat
    username = update.message.from_user.username
    if snapshot.occupant != '':
        context.bot.send_message(chat_id=chat.id, text="Already occupied. Please contact @" + snapshot.occupant)
        return None, None
    return chat, username
