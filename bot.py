import sqlite3
import telebot
from keyboards import get_set_queue_button_keyboard, get_choose_subject_keyboard, current_subject_queue_keyboard, confirmation_keyboard
from api_request import get_subjects, lesson_time
import datetime


subjects = get_subjects()

token = '6408112672:AAFtkvp-Td51vThCAJyUrl5D0Wo55lVuRBY'

bot = telebot.TeleBot(token)


@bot.message_handler(commands=['start'])
def start(message):
    conn = sqlite3.connect('373904.db')
    cur = conn.cursor()
    cur.execute('CREATE TABLE IF NOT EXISTS users (uid int primary key, name varchar(50))')
    conn.commit()

    user_id = message.from_user.id

    cur.execute('SELECT uid FROM users WHERE uid = ?', (user_id,))
    user_exists = cur.fetchone() is not None

    if user_exists:
        markup = get_set_queue_button_keyboard()
        bot.send_message(message.chat.id,
                         f'Привет, {message.from_user.first_name}! Если хочешь занять очередь, нажми на кнопку ниже.',
                         reply_markup=markup)

    else:
        bot.send_message(message.chat.id, f'Привет, {message.from_user.first_name}! К сожалению, тебя пока что нет в системе. Если тебе было '
                                          f'выдано приглашение, но по каким-то причинам ты видишь это сообщение, '
                                          f'напиши @sawatsky')

    cur.close()
    conn.close()


@bot.message_handler(content_types=['text'])
def handler(message):
    if message.text == 'Главное меню':
        markup = get_set_queue_button_keyboard()
        bot.send_message(message.chat.id,
                         f'Привет, {message.from_user.first_name}! Если хочешь занять очередь, нажми на кнопку ниже.',
                         reply_markup=markup)

    if message.text in ['Занять очередь', 'Отмена записи', 'Обмен записями']:
        markup = get_choose_subject_keyboard(subjects)
        global key_message
        key_message = message.text
        bot.send_message(message.chat.id, "Выберите предмет:", reply_markup=markup)

    if message.text in subjects:
        if key_message == 'Занять очередь':
            conn = sqlite3.connect('373904.db')
            cur = conn.cursor()

            cur.execute(f"CREATE TABLE IF NOT EXISTS '{message.text}' (name varchar(50), uid int)")
            conn.commit()

            cur.execute(f"SELECT * FROM '{message.text}' WHERE uid=?", (message.from_user.id,))
            user_already_have_book = cur.fetchone()
            markup = current_subject_queue_keyboard(message.text)

            if user_already_have_book:
                bot.send_message(message.chat.id, "Вы уже записались на эту пару", reply_markup=markup)
            else:
                cur.execute(f"INSERT INTO '{message.text}' (name, uid) VALUES (?, ?)",
                            (message.from_user.first_name, message.from_user.id))
                conn.commit()
                bot.send_message(message.chat.id, f"Вы успешно записаны на {message.text}", reply_markup=markup)

            cur.close()
            conn.close()

        elif key_message == 'Отмена записи':
            global database
            database = message.text

            markup = confirmation_keyboard()
            confirmation_message = bot.send_message(message.chat.id, f'Вы действительно хотите удалить запись на {database}', reply_markup=markup)
            bot.register_next_step_handler(confirmation_message, confirmation_handler)


        #   elif key_message == 'Обмен записями':
        #    sender_name = 1
        #    database = message.text[18:]
        #    conn = sqlite3.connect('373904.db')
        #    cur = conn.cursor()
        #    cur.close()
        #    conn.close()


def confirmation_handler(message):
    if message.text == 'Да':
        conn = sqlite3.connect('373904.db')
        cur = conn.cursor()

        cur.execute(f"DELETE FROM '{database}' WHERE uid = ?", (message.from_user.id,))
        conn.commit()

        cur.close()
        conn.close()

        markup = get_set_queue_button_keyboard()
        bot.send_message(message.chat.id, f'Запись на {database} удалена', reply_markup=markup)

    else:
        markup = get_set_queue_button_keyboard()
        bot.send_message(message.chat.id, f'Запись на {database} не была удалена', reply_markup=markup)


#@bot.message_handler(content_types=['text'])
#def send_message(message):
#    if datetime.datetime.now() == lesson_time():
#        bot.send_message(-1001639367780, message.text)



@bot.callback_query_handler(func=lambda call: True)
def callback(call):
    conn = sqlite3.connect('373904.db')
    cur = conn.cursor()

    current = call.data
    cur.execute(f"SELECT * FROM '{current}'")
    list_all = cur.fetchall()
    info = f'{current}:\n'
    for i, row in enumerate(list_all, 1):
        info += f'{i}. {row[0]}\n'

    cur.close()
    conn.close()

    bot.send_message(call.message.chat.id, info)


if __name__ == '__main__':
    bot.infinity_polling()