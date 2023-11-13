import telebot
from telebot import types
import sqlite3
from api_request import get_subjects

token = '6408112672:AAFtkvp-Td51vThCAJyUrl5D0Wo55lVuRBY'
bot = telebot.TeleBot(token)
user = None
current = None
subjects = get_subjects()


@bot.message_handler(commands=['start'])
def start(message):
    is_valid = False
    conn = sqlite3.connect('373904.db')
    cur = conn.cursor()

    cur.execute('CREATE TABLE IF NOT EXISTS users (id int primary key, name varchar(50))')
    conn.commit()

    global user
    user = message.from_user.first_name
    us_id = message.from_user.id

    cur.execute('SELECT id FROM users')
    ids = cur.fetchall()

    for el in ids:
        if el[0] == us_id:
            is_valid = True

    cur.close()
    conn.close()
    if is_valid:
        bot.register_next_step_handler(message, queue_handler)
    else:
        bot.send_message(message.chat.id, f'Привет, {user}! К сожалению, тебя пока что нет в системе. Если тебе было '
                                          f'выдано приглашение, но по каким-то причинам ты видишь это сообщение, '
                                          f'напиши @sawatsky')


def queue_handler(message):
    global user
    markup = types.ReplyKeyboardMarkup(resize_keyboard=True)
    btn = types.KeyboardButton("Занять очередь")
    markup.add(btn)
    bot.send_message(message.chat.id, f'Привет, {user}! Если хочешь занять очередь, нажми на кнопку ниже.', reply_markup=markup)


@bot.message_handler(content_types=['text'])
def queue_list(message):
    if message.text == 'Занять очередь':
        markup = types.ReplyKeyboardMarkup(resize_keyboard=True)
        for i in range(0, len(subjects), 2):
            if len(subjects) - i == 1:
                markup.add(types.KeyboardButton(subjects[i]))
            else:
                markup.add(types.KeyboardButton(subjects[i]), types.KeyboardButton(subjects[i+1]))
        bot.send_message(message.chat.id, "Выберите предмет:", reply_markup=markup)

    elif message.text in subjects:
        for el in subjects:
            if el == message.text:
                global current
                current = el
                conn = sqlite3.connect('373904.db')
                cur = conn.cursor()

                cur.execute("CREATE TABLE IF NOT EXISTS '%s' (name varchar(50), id int)" % (el))
                conn.commit()

                cur.execute("SELECT * FROM ('%s')" % current)
                check = cur.fetchall()
                flag = True
                if len(check) > 0:
                    if message.from_user.id in check[1]:
                        flag = False
                        bot.send_message(message.chat.id, "Ошибка! Нельзя записаться на один и тот же предмет более одного раза.")
                        break
                if flag:
                    us_id = message.from_user.id
                    user_name = message.from_user.first_name

                    cur.execute("INSERT INTO '%s' (name, id) VALUES (?, ?)" % current, (user_name, us_id))
                    conn.commit()

                    cur.close()
                    conn.close()

                    markup = telebot.types.InlineKeyboardMarkup()
                    markup.add(telebot.types.InlineKeyboardButton('Текущая очередь', callback_data='list'))
                    bot.send_message(message.chat.id, f"Вы успешно записаны на {current}", reply_markup=markup)


@bot.callback_query_handler(func=lambda call: True)
def callback(call):
    global current
    conn = sqlite3.connect('373904.db')
    cur = conn.cursor()

    cur.execute("SELECT * FROM ('%s')" % current)
    list_all = cur.fetchall()
    info = f'{current}:\n'
    for i in range(len(list_all)):
        info += f'{i+1}. {list_all[i][1]}\n'

    cur.close()
    conn.close()

    bot.send_message(call.message.chat.id, info)


if __name__ == '__main__':
    bot.infinity_polling()
