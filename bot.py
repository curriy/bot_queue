import sqlite3
import telebot
from keyboards import get_set_queue_button_keyboard, get_choose_subject_keyboard, current_subject_queue_keyboard, confirmation_keyboard
from api_request import get_subjects
from datetime import datetime

subjects = get_subjects()


def load_token(filename='token.txt'):
    with open(filename, 'r') as file:
        return file.read().strip()


token = load_token()
bot = telebot.TeleBot(token)
DATABASE_NAME = '373904.db'


def init_db():
    with sqlite3.connect(DATABASE_NAME) as conn:
        cur = conn.cursor()
        cur.execute('''CREATE TABLE IF NOT EXISTS records
                       (id INTEGER PRIMARY KEY AUTOINCREMENT,
                        uid INTEGER,
                        subject varchar(50),
                        date varchar(50),
                        subgroup INTEGER NULL)''')

        cur.execute('''CREATE TABLE IF NOT EXISTS users
                       (uid INTEGER,
                        name varchar(50))''')

        conn.commit()


def get_subject_info(subject_name):
    try:
        splitted = subject_name.split(" ")
        if len(splitted) == 3:
            subject, date, subgroup = splitted
            subgroup = int(subgroup[1:-1])
        else:
            subject, date = splitted
            subgroup = None
        return subject, date, subgroup
    except ValueError:
        return None, None, None


def get_record_name(subject):
    return f"{subject[2]} {subject[3]}{f' ({subject[4]})' if subject[4] else ''}"


@bot.message_handler(commands=['start'])
def start(message):
    with sqlite3.connect(DATABASE_NAME) as conn:
        cur = conn.cursor()
        user_id = message.from_user.id
        cur.execute('SELECT uid FROM users WHERE uid = ?', (user_id,))

        record = cur.fetchone()

        if record:
            markup = get_set_queue_button_keyboard()
            bot.send_message(message.chat.id,
                             f"Привет, {message.from_user.first_name}! Если хочешь занять очередь, нажми на кнопку ниже.",
                             reply_markup=markup)
        else:
            bot.send_message(message.chat.id,
                             f"Привет, {message.from_user.first_name}! К сожалению, тебя пока что нет в системе. "
                             f"Если тебе было выдано приглашение, но по каким-то причинам ты видишь это сообщение, "
                             f"напиши @sawatsky")


@bot.message_handler(content_types=['text'])
def handle_text(message):
    user_id = message.from_user.id

    if message.text == 'Главное меню':
        markup = get_set_queue_button_keyboard()
        bot.send_message(message.chat.id,
                         f'Привет, {message.from_user.first_name}! Если хочешь занять очередь, нажми на кнопку ниже.',
                         reply_markup=markup)

    elif message.text == 'Мои записи':
        records = load_user_records(user_id, datetime.now().strftime('%m-%d'))
        response = 'Записи :\n' + '\n'.join([get_record_name(r) for r in records])
        bot.send_message(message.chat.id, response if records else "Нет записей")
    elif message.text == 'Отмена записи':
        markup = get_choose_subject_keyboard(subjects)
        msg = bot.send_message(message.chat.id, "Выберите предмет, запись которого хотите отменить", reply_markup=markup)
        bot.register_next_step_handler(msg, confirmation_handler, 'cancel', user_id)
    elif message.text == 'Занять очередь':
        markup = get_choose_subject_keyboard(subjects)
        bot.send_message(message.chat.id, "Выберите предмет: ", reply_markup=markup)
    elif message.text in subjects:
        subject, date, subgroup = get_subject_info(message.text)

        if not subject:
            bot.send_message(message.chat.id,
                             "Некорректный формат, попробуйте позже")

        markup = current_subject_queue_keyboard(message.text)

        try:
            add_record(user_id, subject, date, subgroup)
            bot.send_message(message.chat.id, f"Запись на {subject} {date} {f'({subgroup})' if subgroup else ''} успешно забронирована", reply_markup=markup)
        except ValueError:
            bot.send_message(message.chat.id, "Вы уже записаны на эту пару.", reply_markup=markup)


def confirmation_handler(message, action, user_id):
    if message.text in subjects and action == 'cancel':
        subject, date, subgroup = get_subject_info(message.text)

        records = load_user_records(user_id, datetime.now().strftime('%m-%d'))

        if not subject:
            bot.send_message(message.chat.id, "Действие отменено.")
            return

        if message.text not in [get_record_name(r) for r in records]:
            bot.send_message(message.chat.id, "У вас нет записи на эту пару")
            return

        with sqlite3.connect(DATABASE_NAME) as conn:
            cur = conn.cursor()
            cur.execute("DELETE FROM records WHERE uid = ? and subject = ? and date = ?", (user_id, subject, date, ))
            conn.commit()
        bot.send_message(message.chat.id, "Запись была отменена.")


@bot.callback_query_handler(func=lambda call: True)
def callback_query(call):
    if call.data.startswith('cancel_record_'):
        record_id = call.data.split('_')[-1]
        with sqlite3.connect(DATABASE_NAME) as conn:
            cur = conn.cursor()
            cur.execute("DELETE FROM records WHERE id = ?", (record_id,))
            conn.commit()
        bot.answer_callback_query(call.id, "Запись отменена.")
        bot.edit_message_text("Запись была успешно отменена.", call.message.chat.id, call.message.message_id)

    if call.data in subjects:
        with sqlite3.connect(DATABASE_NAME) as conn:
            subject, date, subgroup = get_subject_info(call.data)

            if not subject:
                return

            cur = conn.cursor()
            cur.execute("SELECT u.name FROM records r left join users u on u.uid = r.uid WHERE r.subject = ? and r.date = ?", (subject, date))
            records = cur.fetchall()
            records = '\n'.join([f'{index + 1}: {r[0]}' for (index, r) in enumerate(records)])

            text = "Никого нет"

            if records:
                text = f"Текущая очередь: {records}"

            cur.close()
            conn.close()

            bot.send_message(call.message.chat.id, text)


def add_record(uid, subject, date, subgroup):
    with sqlite3.connect(DATABASE_NAME) as conn:
        cur = conn.cursor()

        cur.execute("SELECT * FROM records WHERE uid = ? AND subject = ? and date = ? ORDER BY date ASC", (uid, subject, date))

        if cur.fetchone():
            raise ValueError

        cur.execute("INSERT INTO records (uid, subject, date, subgroup) VALUES (?, ?, ?, ?)",
                    (uid, subject, date, subgroup))
        conn.commit()


def load_user_records(uid, after_date):
    with sqlite3.connect(DATABASE_NAME) as conn:
        cur = conn.cursor()
        cur.execute("SELECT * FROM records WHERE uid = ? AND date > ? ORDER BY date ASC", (uid, after_date))
        return cur.fetchall()


if __name__ == '__main__':
    init_db()
    bot.infinity_polling()

