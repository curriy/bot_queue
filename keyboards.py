from telebot import types


def get_set_queue_button_keyboard():
    markup = types.ReplyKeyboardMarkup(resize_keyboard=True)
    btn = types.KeyboardButton("Занять очередь")
    markup.add(btn)

    return markup


def get_choose_subject_keyboard(subjects):
    markup = types.ReplyKeyboardMarkup(resize_keyboard=True)

    for i in range(0, len(subjects), 2):
        if len(subjects) - i == 1:
            markup.add(types.KeyboardButton(subjects[i]))
        else:
            markup.add(types.KeyboardButton(subjects[i]), types.KeyboardButton(subjects[i + 1]))

    return markup


def current_subject_queue_keyboard(subject):
    markup = types.InlineKeyboardMarkup()
    markup.add(types.InlineKeyboardButton('Текущая очередь', callback_data=subject))

    return markup
