import time
import locale
import psycopg2
import datetime
from psycopg2 import Error
from datetime import datetime
current_datetime = datetime.now()
locale.setlocale(locale.LC_ALL, '')
'ru_RU.utf8'

# print(d.strftime("%I:%M %p"))

try:
    # Подключиться к существующей базе данных
    connection = psycopg2.connect(user="iwannakms",
                                  # пароль, который указали при установке PostgreSQL
                                  password="iwannakms",
                                  host="localhost",
                                  port="5432",
                                  database="tezbus_db")

    # Создайте курсор для выполнения операций с базой данных
    cursor = connection.cursor()

    # SQL-запрос для создания новой таблицы
    # cur = "SELECT * FROM drivers WHERE start_point = %s AND end_point =%s"
    # val = ("Бишкек", "Балыкчы")
    # cur = "SELECT * FROM passengers WHERE start_point = %s AND end_point =%s"
    # val = ("Каракол", "Кант")
    #
    #
    # cursor.execute(cur, val)
    # f = cursor.fetchall()
    # ff = list(f)
    #
    # for i in ff:
    #     t = datetime.strptime(str(i[2]), "%H:%M:%S")
    #     q = str(i[6])
    #     today = datetime.today()
    #     td = today.strftime("%Y-%m-%d")
    #     if q == td:
    #         q = "(Сегодня)"
    #     else:
    #         q = "(Завтра)"
    #
    #     w = datetime.strptime(str(i[6]), "%Y-%m-%d")
    #     res = w.strftime("%d.%m ")+q
    #
    #     print('==========\nКто: Водитель\nОткуда: '+str(i[3])+'\nКуда: '+str(i[5])+'\nКогда: '+res+'\nВремя: '+t.strftime("%H:%M")+'\nТип транспорта: '+str(i[1])+'\nКоличество мест: '+str(i[9])+'\nЦена: '+str(i[7])+'\nКонтакты: '+str(i[8])+'\n==========')
    #     # print('Кто: Водитель\nОткуда: '+t.strftime("%H:%M"))
    #     # print('Кто: Водитель\nОткуда: '+str(i[2])+'\nКуда: '+str(i[3])+'\nКогда: '+str(i[4])+'\nВремя: '+str(i[5])+'\nТип траспорта: '+str(i[6])+'\nКоличество пассажиров: '+str(i[7])+'\nЦена: '+str(i[8])+'\nНомер: '+i[9]+'\n============'+'\n')




    sql = """INSERT INTO drivers (user_id, start_point, end_point, date_of_travel, time_of_travel, number_of_seats, type_of_transport, price_of_travel, telephone)
    VALUES(%s,%s,%s,%s,%s,%s,%s,%s,%s)"""
    val = (99, "q", "w", "2021-08-18", current_datetime, 3, "" )

    cursor.execute(sql, val)

    connection.commit()
    print("Успешно добавлено!")

except (Exception, Error) as error:
    print("Ошибка при работе с PostgreSQL", error)
finally:
    if connection:
        cursor.close()
        connection.close()
        print("Соединение с PostgreSQL закрыто")
