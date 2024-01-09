import sqlite3

# создаем базу данных и устанавливаем соединение с ней
con = sqlite3.connect("library.sqlite")
# открываем файл с дампом базой двнных
f_damp = open('booking.db','r', encoding ='utf-8-sig')
# читаем данные из файла
damp = f_damp.read()
# закрываем файл с дампом
f_damp.close()
# запускаем запросы
con.executescript(damp)
# сохраняем информацию в базе данных
2
con.commit()
# создаем курсор
cursor = con.cursor()

#1
#Для всех номеров, относящихся к типам, названия которых не содержат "люкс",
#и имеющих статус Забронирован в таблице room_booking, вывести информацию об их предполагаемом использовании.
#Для этого указать название номера, дату предполагаемого заселения, количество дней проживания.
#Последний столбец назвать Количество_дней.
#Информацию отсортировать сначала по названию номера в алфавитном порядке, потом по возрастанию даты заселения.
print ('1 задание')
cursor.execute('''SELECT 
        room.room_name AS Название_номера, 
        room_booking.check_in_date AS Дата_заселения, 
        (room_booking.check_out_date - room_booking.check_in_date + 1) AS Количество_дней
    FROM 
        room_booking, room, status, type_room
    WHERE 
        type_room.type_room_name NOT LIKE '%люкс%'
        AND room_booking.room_id = room.room_id
        AND type_room.type_room_id = room.type_room_id
        AND status.status_name = 'Забронирован'
        AND room_booking.status_id = status.status_id
    ORDER BY 
        Название_номера ASC, 
        Дата_заселения ASC;
    ''')
print(cursor.fetchall())
print()

#cursor.execute("SELECT service_name FROM service")
#print(cursor.fetchall())
#print()

#2 задание
print ('2 задание')
cursor.execute('''SELECT 
        service_name AS Услуга,
        COALESCE(COUNT(service_booking.service_id), 0) AS Количество,
        COALESCE(SUM(service_booking.price), 0) AS Сумма
    FROM
        service_booking 
    RIGHT JOIN service
    ON service.service_id = service_booking.service_id
    GROUP BY Услуга
    ORDER BY Сумма DESC, Количество DESC, Услуга ASC;
''')

print(cursor.fetchall())
print()

#3 Вывести номера,относящиеся к тому типу(ам) номера(ов),
# в котором(ых) проживало больше всего гостей
print ('3 задание')
cursor.execute('''
    SELECT
    type,
    MAX(count),
    room_numbers
    FROM (SELECT
        type_room.type_room_name AS type,
        COUNT(*) AS count,
        GROUP_CONCAT(room_name, ', ') AS room_numbers
        FROM room, type_room
        JOIN room_booking ON room.room_id = room_booking.room_id
        WHERE room.type_room_id = type_room.type_room_id
        GROUP BY type
        ORDER BY type ASC, room_numbers DESC)
''')

print(cursor.fetchall())
print()

#4
# Изменить статус бронирования номера
print('4 задание')
query_update_room_booking = '''UPDATE room_booking
            SET status_id = (SELECT status_id FROM status WHERE status_name = 'Бронирование отменено')
            WHERE guest_id = (SELECT guest_id FROM guest WHERE guest_name = 'Жидкова Р.Л.')
            AND room_id = (SELECT room_id FROM room WHERE room_name = 'П-1004')
            AND check_in_date = '2021-06-01'
            '''
cursor.execute(query_update_room_booking)
print('Изменен статус бронирования')
cursor.execute('''
    SELECT *
    FROM status   
''')
print(cursor.fetchall())
print()
cursor.execute('''
    SELECT *
    FROM room_booking
    WHERE room_booking.guest_id = (SELECT guest_id FROM guest WHERE guest_name = 'Жидкова Р.Л.')
            
''')
print(cursor.fetchall())
print()


# Удалить услуги из таблицы service_booking
query_delete_services = '''DELETE FROM service_booking
                WHERE
                room_booking_id = (SELECT room_booking_id FROM room_booking WHERE
                room_id = (SELECT room_id FROM room WHERE room_name = 'П-1004')
                AND check_in_date = '2021-06-01')
                
                '''
cursor.execute(query_delete_services)
#5
print('5 задание')

# Формируем SQL запрос с использованием оконных функций для определения свободных номеров на указанные даты
query = '''
SELECT r.room_name
FROM room r
LEFT JOIN room_booking rb ON r.room_id = rb.room_id
AND rb.check_in_date <= '2021-02-16' AND rb.check_out_date >= '2020-12-11'
WHERE r.type_room_id = (SELECT type_room_id
FROM type_room WHERE type_room_name = 'Стандартный одноместный номер')
AND rb.room_id IS NULL
ORDER BY r.room_id;
'''

cursor.execute(query)

# Выводим номера комнат, которые свободны на указанные даты и отсортированы по алфавиту
print(cursor.fetchall())
print()

# Подтвердить изменения
con.commit()

# закрываем соединение с базой
con.close()

