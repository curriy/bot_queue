from telebot import types


def get_set_queue_button_keyboard():
    markup = types.ReplyKeyboardMarkup(resize_keyboard=True)
    btn1 = types.KeyboardButton("Занять очередь", )
    btn2 = types.KeyboardButton("Отмена записи")
    # btn4 = types.KeyboardButton("Обмен записями")
    btn3 = types.KeyboardButton("Мои записи")

    markup.add(btn1, btn2)
    markup.add(btn3)

    return markup


def get_choose_action_keyboard(subject):
    markup = types.ReplyKeyboardMarkup(resize_keyboard=True)
    btn = types.KeyboardButton(f"Отменить очередь на {subject}")
    markup.add(btn)

    return markup


def confirmation_keyboard():
    markup = types.ReplyKeyboardMarkup(resize_keyboard=True)
    btn1 = types.KeyboardButton("Да")
    btn2 = types.KeyboardButton("Нет")
    markup.add(btn1, btn2)

    return markup


def get_choose_subject_keyboard(subjects):
    markup = types.ReplyKeyboardMarkup(resize_keyboard=True)

    for i in range(0, len(subjects), 2):
        if len(subjects) - i == 1:
            markup.add(types.KeyboardButton(subjects[i]))
        else:
            markup.add(types.KeyboardButton(subjects[i]), types.KeyboardButton(subjects[i + 1]))

    markup.add(types.KeyboardButton("Главное меню"))

    return markup


def current_subject_queue_keyboard(subject):
    markup = types.InlineKeyboardMarkup()
    markup.add(types.InlineKeyboardButton('Текущая очередь', callback_data=subject))

    return markup
