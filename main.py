import sys
import traceback
import os
import telebot
import collections
from flask import Flask, request
from telebot import *
import re
import locale
import psycopg2
import time
import datetime
from datetime import datetime, timedelta


connection = psycopg2.connect(
user="iwannakms",
password="iwannakms",
host="localhost",
port="5432",
database="tezbus_db"
)

cursor = connection.cursor()
# mycursor = mydb.cursor()



TOKEN = "1794881977:AAFtVmJ2etRkwrRK1KxYzc_AOcIywuHodyU"
APP_URL = f"https://tezbusbot.herokuapp.com/"
bot = telebot.TeleBot(TOKEN)
server = Flask(__name__)


print("Started...")


user_data = collections.defaultdict(dict)


@bot.message_handler(commands=['start'])
def send_welcome(message):
    markup = types.ReplyKeyboardMarkup(resize_keyboard=True)
    markup.add('/kettik')
    user_data[message.chat.id]['id'] = message.chat.id
    bot.send_message(message.chat.id, "бот TezBus приветствует вас!")
    bot.send_message(message.chat.id, "Нажмите на /kettik для того, чтобы начать.", reply_markup=markup)
    print(message.chat.id)


#ОБРАБОТКА РОЛИ ПОЛЬЗОВАТЕЛЯ
@bot.message_handler(commands=['kettik'])
def get_user_role(message):
    bot.send_message(message.chat.id, '🚗')
    markup = types.ReplyKeyboardMarkup(resize_keyboard=True, one_time_keyboard=True)
    markup.add('🚗Водитель', '💁Пассажир')
    bot.send_message(message.chat.id, "Кто вы?", reply_markup=markup)

    bot.register_next_step_handler(message, post_user_role)


@bot.message_handler(content_types=['text'])
def post_user_role(message):
    if message.text.lower()[1:] == 'водитель' or message.text.lower()[1:] == 'пассажир':
        user_data[message.chat.id]['role'] = message.text[1:]
        return get_start_point(message) #ПЕРЕХОДИМ В ВВОДУ МЕСТА НАЧАЛА ПОЕЗДКИ
    else:
        bot.send_message(message.chat.id, '❌ОШИБКА!❌ Введите заново.')
        return get_user_role(message) #ЗАНОВО ПЕРЕХОДИМ К ВВОДУ РОЛИ ПОЛЬЗОВАТЕЛЯ

@server.route('/' + TOKEN, methods=['POST'])
def get_message():
    json_string = request.get_data().decode('utf-8')
    update = telebot.types.Update.de_json(json_string)
    bot.process_new_updates([update])
    return '!', 200


@server.route('/')
def webhook():
    bot.remove_webhook()
    bot.set_webhook(url=APP_URL)
    return '!', 200

def reinput_user_role(message):
    if message.text.lower() == '↩️ввести заново роль':
        return get_user_role(message)

    return post_start_point(message)


#ОБРАБОТКА МЕСТА НАЧАЛА ПОЕЗДКИ
def get_start_point(message):
    start_point_markup = types.ReplyKeyboardMarkup(resize_keyboard=True)
    start_point_markup.add('↩️Ввести заново роль')
    bot.send_message(message.chat.id, '📍Введите место начала поездки(Город или Село)', reply_markup=start_point_markup)
    bot.register_next_step_handler(message, reinput_user_role)


def post_start_point(message):
    user_data[message.chat.id]['start_point'] = re.sub(r"\d+", "", message.text, flags=re.UNICODE)
    return get_end_point(message)


def reinput_start_point(message):
    if message.text.lower() == '↩️ввести заново место начала поездки':
        return get_start_point(message)

    return post_end_point(message)


#ОБРАБОТКА МЕСТА КОНЦА ПОЕЗДКИ
def get_end_point(message):
    end_pont_markup = types.ReplyKeyboardMarkup(resize_keyboard=True)
    end_pont_markup.add('↩️Ввести заново место начала поездки')
    bot.send_message(message.chat.id, '📌Введите место конца поездки(Город или Село)', reply_markup=end_pont_markup)
    bot.register_next_step_handler(message, reinput_start_point)


def post_end_point(message):
    if user_data[message.chat.id]['start_point'].lower() != message.text.lower():
        user_data[message.chat.id]['end_point'] = re.sub(r"\d+", "", message.text, flags=re.UNICODE)
    else:
        bot.send_message(message.chat.id, '❌ОШИБКА!❌ Место конца поездки не может быть таким же, что и место начала поездки. Введите заново')
        return get_end_point(message)

    return get_date_of_travel(message)


def reinput_end_point(message):
    if message.text.lower() == '↩️ввести заново место конца поездки':
        return get_end_point(message)

    return post_date_of_travel(message)


#ОБРАБОТКА ДАТЫ ПОЕЗДКИ
def get_date_of_travel(message):
    date_markup = types.ReplyKeyboardMarkup(resize_keyboard=True)
    date_markup.add('🔛Сегодня', '🔜Завтра', '↩️Ввести заново место конца поездки')
    bot.send_message(message.chat.id, 'Ввыберите дату поездки', reply_markup=date_markup)
    bot.register_next_step_handler(message, reinput_end_point)


def post_date_of_travel(message):

    today = datetime.today()
    tomorrow = today + timedelta(days=1)

    if message.text.lower()[1:] == 'сегодня':
        user_data[message.chat.id]['date_of_travel1'] = today.strftime('%d.%m.') + " ( Сегодня )"
        user_data[message.chat.id]['date_of_travel'] = user_data[message.chat.id]['date_of_travel1']
        user_data[message.chat.id]['date_of_travel'] = today.strftime('%Y-%m-%d')

    else:
        user_data[message.chat.id]['date_of_travel1'] = tomorrow.strftime('%d.%m.') + " ( Завтра )"
        user_data[message.chat.id]['date_of_travel'] = user_data[message.chat.id]['date_of_travel1']
        user_data[message.chat.id]['date_of_travel'] = tomorrow.strftime('%Y-%m-%d')

    return get_time_of_travel(message)



def reinput_date_of_travel(message):
    if message.text.lower() == '↩️ввести заново дату поездки':
        return get_date_of_travel(message)

    return post_time_of_travel(message)


#ОБРАБОТКА ВРЕМЕНИ ПОЕЗДКИ
def get_time_of_travel(message):
    time_markup = types.ReplyKeyboardMarkup(resize_keyboard=True)
    time_markup.add('↩️Ввести заново дату поездки')
    bot.send_message(message.chat.id, '🕰Введите время поездки🕰', reply_markup=time_markup)
    bot.register_next_step_handler(message, reinput_date_of_travel)


def post_time_of_travel(message):
    user_data[message.chat.id]['time_of_travel'] = message.text
    return get_type_of_transport(message)


def reinput_time_of_travel(message):
    if message.text.lower() == '↩️ввести заново время поездки':
        return get_date_of_travel(message)

    return post_type_of_transport(message)


#ОБРАБОТКА ТИПА ТРАНСПОРТА ПОЛЬЗОВАТЕЛЯ
def get_type_of_transport(message):
    type_markup = types.ReplyKeyboardMarkup(resize_keyboard=True)
    if user_data[message.chat.id]['role'].lower() == 'пассажир' and user_data[message.chat.id]['start_point'].lower() == 'бишкек' and user_data[message.chat.id]['end_point'].lower() == 'балыкчы' or user_data[message.chat.id]['end_point'].lower() == 'рыбачье':
        type_markup.add('🚘машина', '🚍автобус', '🚆поезд', '↩️ввести заново время поездки')
    elif user_data[message.chat.id]['role'].lower() == 'пассажир' and user_data[message.chat.id]['start_point'].lower() == 'бишкек' and user_data[message.chat.id]['end_point'].lower() == 'токмок':
        type_markup.add('🚘машина', '🚍автобус', '🚆поезд', '↩️ввести заново время поездки')
    elif user_data[message.chat.id]['role'].lower() == 'пассажир' and user_data[message.chat.id]['start_point'].lower() == 'бишкек' and user_data[message.chat.id]['end_point'].lower() == 'каинды' or user_data[message.chat.id]['end_point'].lower() == 'каиңды':
        type_markup.add('🚘машина', '🚍автобус', '🚆поезд', '↩️ввести заново время поездки')

    elif user_data[message.chat.id]['role'].lower() == 'пассажир' and user_data[message.chat.id]['start_point'].lower() == 'балыкчы' or user_data[message.chat.id]['start_point'].lower() == 'балыкчи' or user_data[message.chat.id]['start_point'].lower() == 'рыбачье' and user_data[message.chat.id]['end_point'].lower() == 'бишкек':
        type_markup.add('🚘машина', '🚍автобус', '🚆поезд', '↩️ввести заново время поездки')
    elif user_data[message.chat.id]['role'].lower() == 'пассажир' and user_data[message.chat.id]['start_point'].lower() == 'токмок' and user_data[message.chat.id]['end_point'].lower() == 'бишкек':
        type_markup.add('🚘машина', '🚍автобус', '🚆поезд', '↩️ввести заново время поездки')
    elif user_data[message.chat.id]['role'].lower() == 'пассажир' and user_data[message.chat.id]['start_point'].lower() == 'каинды' or user_data[message.chat.id]['start_point'].lower() == 'каиңды' and user_data[message.chat.id]['end_point'].lower() == 'бишкек':
        type_markup.add('🚘машина', '🚍автобус', '🚆поезд', '↩️ввести заново время поездки')

    else:
        type_markup.add('🚘машина', '🚍автобус', '↩️ввести заново время поездки')

    bot.send_message(message.chat.id, 'Введите тип транспорта.', reply_markup=type_markup)
    bot.register_next_step_handler(message, reinput_time_of_travel)


def post_type_of_transport(message):
    if user_data[message.chat.id]['role'].lower == 'водитель':
        if message.text.lower()[1:] == 'машина' or message.text.lower()[1:] == 'автобус':
            user_data[message.chat.id]['type_of_transport'] = message.text[1:]
            return get_number_of_seats(message)
        else:
            bot.send_message(message.chat.id, '❌ОШИБКА!❌ Введите заново')
            return get_type_of_transport(message)
    else:
        if message.text.lower()[1:] == 'машина' or message.text.lower()[1:] == 'автобус' or message.text.lower()[1:] == 'поезд':
            user_data[message.chat.id]['type_of_transport'] = message.text[1:]
            return get_number_of_seats(message)
        else:
            bot.send_message(message.chat.id, '❌ОШИБКА!❌ Введите заново')
            return get_type_of_transport(message)


def reinput_type_of_transport(message):
    if message.text.lower() == '↩️ввести заново тип транспорта':
        return get_type_of_transport(message)

    return post_number_of_seats(message)


#ОБРАБОТКА КОЛИЧЕСТВ МЕСТ
def get_number_of_seats(message):
    seats_markup = types.ReplyKeyboardMarkup(resize_keyboard=True)
    seats_markup.add('1', '2', '3', '4', '5', '6', '↩️ввести заново тип транспорта')
    bot.send_message(message.chat.id, '💺Введите количество мест.', reply_markup=seats_markup)
    bot.register_next_step_handler(message, reinput_type_of_transport)


def post_number_of_seats(message):
    if message.text.isdigit():
        user_data[message.chat.id]['number_of_seats'] = int(message.text)
        return get_price_of_travel(message)
    else:
        bot.send_message(message.chat.id, '❌ОШИБКА!❌ Введите заново')
        return get_number_of_seats(message)


def reinput_number_of_seats(message):
    if message.text.lower() == '↩️ввести заново количество мест':
        return get_number_of_seats(message)

    return post_price_of_travel(message)


#ОБРАБОТКА ЦЕНЫ ПОЕЗДКИ
def get_price_of_travel(message):
    price_markup = types.ReplyKeyboardMarkup(resize_keyboard=True)
    price_markup.add('↩️ввести заново количество мест')
    bot.send_message(message.chat.id, 'Введите цену поездки с человека (сом).', reply_markup=price_markup)
    bot.register_next_step_handler(message, reinput_number_of_seats)


def post_price_of_travel(message):

    if message.text.isdigit():
        user_data[message.chat.id]['price_of_travel'] = message.text
        return get_telephone(message)
    else:
        bot.send_message(message.chat.id, '❌ОШИБКА!❌ Введите заново')
        return get_price_of_travel(message)


def reinput_price_of_travel(message):
    if message.text.lower() == '↩️ввести заново цену поездки':
        return get_price_of_travel(message)

    return post_telephone(message)


#ОБРАБОТКА НОМЕРА ТЕЛЕФОНА
def get_telephone(message):
    telephone_markup = types.ReplyKeyboardMarkup(resize_keyboard=True)
    telephone_markup.add('↩️ввести заново цену поездки')
    bot.send_message(message.chat.id, '📞Введите ваш номер телефона.', reply_markup=telephone_markup)
    bot.register_next_step_handler(message, reinput_price_of_travel)


def post_telephone(message):
    user_data[message.chat.id]['telephone'] = message.text
    return final(message)


def reinput_telephone(message):
    if message.text.lower() == '↩️ввести заново номер телефона':
        return get_telephone(message)

    return get_result(message)


#РЕЗУЛЬТАТ
def final(message):
    final_markup = types.ReplyKeyboardMarkup(resize_keyboard=True)
    final_markup.add('📝Завершить регистрацию', '↩️ввести заново номер телефона')
    bot.send_message(message.chat.id, '📝Хотите завершить регистрацию?', reply_markup=final_markup)
    bot.register_next_step_handler(message, reinput_telephone)


#РЕКОМЕНДАЦИИ
def get_result(message):
    result_markup = types.ReplyKeyboardMarkup(resize_keyboard=True)
    result_markup.add('получить рекомендации', 'нет')
    bot.send_message(message.chat.id, 'Регистрация прошла успешно!\nВаш пост:')
    bot.send_message(message.chat.id, f"Человек: {user_data[message.chat.id]['role']}\nМесто начала поездки: {user_data[message.chat.id]['start_point']}\nМесто конца поездки: {user_data[message.chat.id]['end_point']}\nДата поездки: {user_data[message.chat.id]['date_of_travel1']}\nВремя поездки: {user_data[message.chat.id]['time_of_travel']}\nТип транспорта: {user_data[message.chat.id]['type_of_transport']}\nКоличество мест: {user_data[message.chat.id]['number_of_seats']}\nЦана поездки: {user_data[message.chat.id]['price_of_travel']}\nКонтакты: {user_data[message.chat.id]['telephone']}")
    if user_data[message.chat.id]['type_of_transport'] =='поезд':
        bot.register_next_step_handler(message, send_result)
    else:
        bot.send_message(message.chat.id, 'Хотите получить рекомендации?', reply_markup=result_markup)
        bot.register_next_step_handler(message, send_recommendations)


def send_recommendations(message):
    if message.text.lower() == 'получить рекомендации':
        bot.send_message(message.chat.id, "🔎")
        time.sleep(4)
        if user_data[message.chat.id]['role'] == "Пассажир":
            sql = "SELECT * FROM drivers WHERE start_point = %s AND end_point = %s AND date_of_travel = %s"
            val = (user_data[message.chat.id]['start_point'], user_data[message.chat.id]['end_point'], user_data[message.chat.id]['date_of_travel'],)
            cursor.execute(sql, val)
            myresult_1 = cursor.fetchall()
            myresult = list(myresult_1)
            for i in myresult:
                t = datetime.strptime(str(i[2]), "%H:%M:%S")
                q = str(i[6])
                today = datetime.today()
                td = today.strftime("%Y-%m-%d")
                if q == td:
                    q = "(Сегодня)"
                else:
                    q = "(Завтра)"
                w = datetime.strptime(str(i[6]), "%Y-%m-%d")
                res = w.strftime("%d.%m ")+q
                bot.send_message(message.chat.id, '==========\nКто: Водитель\nОткуда: '+str(i[3])+'\nКуда: '+str(i[5])+'\nКогда: '+res+'\nВремя: '+t.strftime("%H:%M")+'\nТип транспорта: '+str(i[1])+'\nКоличество мест: '+str(i[9])+'\nЦена: '+str(i[7])+'\nКонтакты: '+str(i[8])+'\n==========')
        else:
            sql = "SELECT * FROM passengers WHERE start_point = %s AND end_point = %s AND date_of_travel = %s "
            val = (user_data[message.chat.id]['start_point'], user_data[message.chat.id]['end_point'], user_data[message.chat.id]['date_of_travel'],)
            cursor.execute(sql, val)
            myresult_1 = cursor.fetchall()
            myresult = list(myresult_1)
            for i in myresult:
                t = datetime.strptime(str(i[2]), "%H:%M:%S")
                q = str(i[6])
                today = datetime.today()
                td = today.strftime("%Y-%m-%d")
                if q == td:
                    q = "(Сегодня)"
                else:
                    q = "(Завтра)"
                w = datetime.strptime(str(i[6]), "%Y-%m-%d")
                res = w.strftime("%d.%m ")+q
                bot.send_message(message.chat.id, '==========\nКто: Пассажир\nОткуда: '+str(i[3])+'\nКуда: '+str(i[5])+'\nКогда: '+res+'\nВремя: '+t.strftime("%H:%M")+'\nТип транспорта: '+str(i[1])+'\nКоличество мест: '+str(i[9])+'\nЦена: '+str(i[7])+'\nКонтакты: '+str(i[8])+'\n==========')

    return send_result(message)


#ФИНАЛ
def send_result(message):
    post_markup = types.ReplyKeyboardMarkup(resize_keyboard=True)
    post_markup.add('отправить','нет')
    bot.send_message(message.chat.id,"📝")
    if user_data[message.chat.id]['type_of_transport'] =='поезд':
        if user_data[message.chat.id]['start_point'].lower() == 'бишкек' and user_data[message.chat.id]['end_point'].lower() == 'балыкчы' \
                or user_data[message.chat.id]['end_point'].lower() == 'рыбачье' and user_data[message.chat.id]['start_point'].lower() == 'балыкчы' \
                or user_data[message.chat.id]['start_point'].lower() == 'балыкчи' or user_data[message.chat.id]['start_point'].lower() == 'рыбачье' \
                and user_data[message.chat.id]['end_point'].lower() == 'бишкек':
            bot.send_message(message.chat.id, """Поезд “Бишкек-Рыбачье”, “Рыбачье-Бишкек”.
Время указано местное.
С 15-июля по 31-августа 2021 года ежедневно.
Поезд №608 “Бишкек I – Рыбачье” время отправления по местному времени со станции «Бишкек I» (Пишпек) в 07 часов 00 минут, время прибытия на станцию Рыбачье в 11 часов 59 минут.
Поезд №609 “Рыбачье – Бишкек I»  время отправления по местному времени со станции «Рыбачье» в 17 часов 15 минут, время прибытия на станцию «Бишкек I» (Пишпек) в 22 часа 03 минуты.
Стоимость проезда:
Взрослый билет: 69 сом
Детский билет: 34 сом  (от 5 до 10 лет)
 """)
        elif user_data[message.chat.id]['start_point'].lower() == 'бишкек' and user_data[message.chat.id]['end_point'].lower() == 'токмок' \
                or user_data[message.chat.id]['start_point'].lower() == 'токмок' \
                and user_data[message.chat.id]['end_point'].lower() == 'бишкек':
            bot.send_message(message.chat.id, """ Пригородный  поезд «Бишкек-Токмок», «Токмок-Бишкек»
Время указано местное.
Поезд №6050 “Бишкек I – Токмок” время отправления по местному времени со станции “Бишкек I» (Пишпек) в 17 часов 20 минут, время прибытия на станцию Токмок в 19 часов 35 минут.
Поезд №6051 “Токмок - Бишкек I” время отправления по местному времени со станции «Токмок» в 05 часов 05 минут, время прибытия на станцию “Бишкек I” (Пишпек) в 07 часов 21 минуту.
Стоимость проезда:
Взрослый билет: 26 сом
Детский билет: 9 сом  (от 5 до 10 лет)""")
        elif user_data[message.chat.id]['start_point'].lower() == 'бишкек' and user_data[message.chat.id]['end_point'].lower() == 'каинды' \
                or user_data[message.chat.id]['end_point'].lower() == 'каиңды' and user_data[message.chat.id]['start_point'].lower() == 'каиңды' \
                or user_data[message.chat.id]['start_point'].lower() == 'каинды'\
                and user_data[message.chat.id]['end_point'].lower() == 'бишкек':
            bot.send_message(message.chat.id,""" Пригородный  поезд «Бишкек-Каинды», «Каинды-Бишкек»
Время указано местное.
Поезд №6063 “Бишкек II - Каинды” время отправления по местному времени со станции «Бишкек II» в 17 часов 31 минуту, время прибытия на станцию «Каинды» в 20 часов 06 минут.
Поезд №6064 “Каинды - Бишкек II” время отправления по местному времени со станции «Каинды» в 05 часов 07 минут, время прибытия на  станцию “Бишкек II” в 07 часов 32 минуты.
Стоимость проезда:
Взрослый билет: 26 сом
Детский билет: 9 сом  (от 5 до 10 лет)""")

        markup = types.ReplyKeyboardRemove(selective=False)

        bot.send_message(message.chat.id, 'Нажмите на /kettik для того, чтобы начать.', reply_markup=markup)
    else:
        bot.send_message(message.chat.id, 'Хотите отправить ваш пост в группу?', reply_markup=post_markup)
        bot.register_next_step_handler(message, post_message)

    if user_data[message.chat.id]['role'] =='Водитель':
        sql = """INSERT INTO drivers (user_id, start_point, end_point, date_of_travel, time_of_travel, type_of_transport, number_of_seats, price_of_travel, telephone) VALUES(%s,%s,%s,%s,%s,%s,%s,%s,%s)"""
        val = (user_data[message.chat.id]['id'], user_data[message.chat.id]['start_point'], user_data[message.chat.id]['end_point'], user_data[message.chat.id]['date_of_travel'], user_data[message.chat.id]['time_of_travel'], user_data[message.chat.id]['type_of_transport'], user_data[message.chat.id]['number_of_seats'], user_data[message.chat.id]['price_of_travel'], user_data[message.chat.id]['telephone'])
        cursor.execute(sql, val)
        connection.commit()
    else:
        sql = """INSERT INTO passengers (user_id, start_point, end_point, date_of_travel, time_of_travel, type_of_transport, number_of_seats, price_of_travel, telephone) VALUES(%s,%s,%s,%s,%s,%s,%s,%s,%s)"""
        val = (user_data[message.chat.id]['id'], user_data[message.chat.id]['start_point'], user_data[message.chat.id]['end_point'], user_data[message.chat.id]['date_of_travel'], user_data[message.chat.id]['time_of_travel'], user_data[message.chat.id]['type_of_transport'], user_data[message.chat.id]['number_of_seats'], user_data[message.chat.id]['price_of_travel'], user_data[message.chat.id]['telephone'])
        cursor.execute(sql, val)
        connection.commit()

def post_message(message):
    if message.text.lower() == 'отправить':
        bot.send_message(-1001561468463, f"Кто: {user_data[message.chat.id]['role']}\nОткуда: {user_data[message.chat.id]['start_point']}\nКуда: {user_data[message.chat.id]['end_point']}\nКогда: {user_data[message.chat.id]['date_of_travel1']}\nВремя: {user_data[message.chat.id]['time_of_travel']}\nТип транспорта: {user_data[message.chat.id]['type_of_transport']}\nКоличество мест: {user_data[message.chat.id]['number_of_seats']}\nЦана: {user_data[message.chat.id]['price_of_travel']}\nКонтакты: {user_data[message.chat.id]['telephone']}")
        markup = types.ReplyKeyboardRemove(selective=False)
        bot.send_message(message.chat.id, 'Ваш пост отправлен!', reply_markup=markup)
        bot.send_message(message.chat.id, 'Нажмите на /kettik для того, чтобы начать.', reply_markup=markup)
    else:
        markup = types.ReplyKeyboardRemove(selective=False)
        bot.send_message(message.chat.id, 'Нажмите на /kettik для того, чтобы начать.', reply_markup=markup)



bot.enable_save_next_step_handlers(delay=2)
bot.load_next_step_handlers()

bot.infinity_polling()
