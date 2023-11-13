import sqlite3
import telebot
from utils.keyboards import get_set_queue_button_keyboard, get_choose_subject_keyboard, current_subject_queue_keyboard

from api_request import get_subjects

subjects = get_subjects()

with open('token.txt', 'r') as token_file:
    token = token_file.read().strip()

bot = telebot.TeleBot(token)


@bot.message_handler(commands=['start'])
def start(message):
    conn = sqlite3.connect('373904.db')
    cur = conn.cursor()
    cur.execute('CREATE TABLE IF NOT EXISTS users (id int primary key, name varchar(50))')
    conn.commit()

    user_id = message.from_user.id

    cur.execute('SELECT id FROM users WHERE id = ?', (user_id,))
    user_exists = cur.fetchone() is not None

    if user_exists:
        bot.register_next_step_handler(message, get_queue)
    else:
        bot.send_message(message.chat.id, f'Привет, {message.from_user.first_name}! К сожалению, тебя пока что нет в системе. Если тебе было '
                                          f'выдано приглашение, но по каким-то причинам ты видишь это сообщение, '
                                          f'напиши @sawatsky')
    cur.close()
    conn.close()


def get_queue(message):
    markup = get_set_queue_button_keyboard()
    bot.send_message(message.chat.id, f'Привет, {message.from_user.first_name}! Если хочешь занять очередь, нажми на кнопку ниже.', reply_markup=markup)


@bot.message_handler(content_types=['text'])
def handler(message):
    if message.text == 'Занять очередь':
        markup = get_choose_subject_keyboard(subjects)
        bot.send_message(message.chat.id, "Выберите предмет:", reply_markup=markup)
    elif message.text in subjects:
        conn = sqlite3.connect('373904.db')
        cur = conn.cursor()

        cur.execute(f"CREATE TABLE IF NOT EXISTS '{message.text}' (name varchar(50), id int)")
        conn.commit()

        cur.execute(f"SELECT * FROM '{message.text}' WHERE id=?", (message.from_user.id,))
        user_already_have_book = cur.fetchone()
        markup = current_subject_queue_keyboard(message.text)

        if user_already_have_book:
            bot.send_message(message.chat.id, "Вы уже записались на эту пару", reply_markup=markup)
        else:
            cur.execute(f"INSERT INTO '{message.text}' (name, id) VALUES (?, ?)", (message.from_user.first_name, message.from_user.id))
            conn.commit()

            bot.send_message(message.chat.id, f"Вы успешно записаны на {message.text}", reply_markup=markup)

        cur.close()
        conn.close()


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
