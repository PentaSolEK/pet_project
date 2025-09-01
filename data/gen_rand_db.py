import os
from datetime import datetime, timedelta

import pymysql
from dotenv import load_dotenv
from faker import Faker
import random

# Инициализация Faker
fake = Faker('ru_RU')

<<<<<<< HEAD
load_dotenv(r"/data/.env")
=======
load_dotenv(r"C:\Users\pazhi\PycharmProjects\projects\.venv\concert_app\data\CONCERT_DB.env")
>>>>>>> b05e70515c495ef1fdffd9205744cc93d4447f51

DB_USER = os.getenv('DB_USER')
DB_PASSWORD = os.getenv('DB_PASSWORD')
DB_HOST = os.getenv('DB_HOST')
DB_NAME = os.getenv('DB_NAME')

# Подключение к базе данных
connection = pymysql.connect(
    host=DB_HOST,
    user=DB_USER,
    password=DB_PASSWORD,
    database=DB_NAME,
    charset='utf8mb4',
    cursorclass=pymysql.cursors.DictCursor
)

try:
    with connection.cursor() as cursor:
        """Заполнить таблицу concert"""
        # concert_types = [
        #     "Rock", "Jazz", "Pop", "Classical", "Hip-Hop",
        #     "Electronic", "Metal", "Folk", "Blues", "R&B",
        #     "Indie", "Alternative", "Punk", "Reggae", "Country"
        # ]
        #
        # concert_formats = [
        #     "Festival", "Concert", "Night", "Live", "Show",
        #     "Experience", "Session", "Gig", "Performance", "Tour"
        # ]
        # start_date = datetime(2025, 6, 1)
        # end_date = datetime(2026, 12, 31)
        #
        # # Обновляем каждую запись случайной датой
        # for i in range(20):
        #     name = f"{random.choice(concert_types)} {random.choice(concert_formats)}"
        #     random_date = start_date + timedelta(
        #         seconds=random.randint(0, int((end_date - start_date).total_seconds())
        #                                ))
        #
        #     id_hall = random.randint(12, 31)
        #
        #     insert_query = """
        #                 INSERT INTO concert (name, date, id_hall)
        #                 VALUES (%s, %s, %s)
        #                 """
        #     cursor.execute(insert_query, (name, random_date, id_hall))

        """Вставка данных в hall_tickettypes"""
        # 1. Получаем информацию о залах из таблицы Hall
        cursor.execute("SELECT number, seatsAmount FROM Hall")
        halls = cursor.fetchall()

        # 2. Подготавливаем данные для вставки
        ticket_data = []

        for hall in halls:
            hall_id = hall['number']
            max_seats = hall['seatsAmount']

            # Создаем 3 типа билетов для каждого зала
            for ticket_type in range(1, 4):
                # Генерируем количество билетов (от 100 до seatsAmount)
                amount = random.randint(100, max_seats)

                ticket_data.append((
                    amount,
                    hall_id,
                    ticket_type
                ))


        # 3. Вставляем данные в таблицу
        insert_query = """
                INSERT INTO hall_tickettypes (amount, id_hall, id_type)
                VALUES (%s, %s, %s)
                """
        cursor.executemany(insert_query, ticket_data)

        """Заполянем tickets"""
        # # 1. Получаем все концерты с их залами
        # cursor.execute("""
        #         SELECT c.id_concert, c.id_hall
        #         FROM concert c
        #         JOIN hall h ON c.id_hall = h.number
        #         """)
        # concerts = cursor.fetchall()
        #
        # # 2. Получаем все типы билетов с их залами
        # cursor.execute("""
        #         SELECT ht.id_hall_ticketTypes as id_hall_ticketTypes, ht.id_hall
        #         FROM hall_tickettypes ht
        #         """)
        # ticket_types = cursor.fetchall()
        #
        # # 3. Группируем типы билетов по id_hall
        # ticket_types_by_hall = {}
        # for tt in ticket_types:
        #     if tt['id_hall'] not in ticket_types_by_hall:
        #         ticket_types_by_hall[tt['id_hall']] = []
        #     ticket_types_by_hall[tt['id_hall']].append(tt['id_hall_ticketTypes'])
        #
        # # 4. Генерируем данные для таблицы tickets
        # tickets_data = []
        # current_id = 4  # Продолжаем после существующих записей
        #
        # for concert in concerts:
        #     concert_id = concert['id_concert']
        #     hall_id = concert['id_hall']
        #
        #     # Проверяем, есть ли типы билетов для этого зала
        #     if hall_id in ticket_types_by_hall:
        #         # Берем случайные 1-3 типа билетов для этого концерта
        #         num_ticket_types = random.randint(1, min(3, len(ticket_types_by_hall[hall_id])))
        #         selected_types = random.sample(ticket_types_by_hall[hall_id], num_ticket_types)
        #
        #         for ticket_type_id in selected_types:
        #             tickets_data.append((
        #                 concert_id,
        #                 ticket_type_id
        #             ))
        #             current_id += 1
        #
        # # 5. Вставляем данные в таблицу tickets
        # insert_query = """
        #         INSERT INTO tickets (id_concert, id_hall_ticketTypes)
        #         VALUES (%s, %s)
        #         """
        # cursor.executemany(insert_query, tickets_data)
        # connection.commit()

        """"заполнение sales"""
        # Получаем существующие ID пользователей и билетов
        # cursor.execute("SELECT id_user FROM Users")
        # user_ids = [row['id_user'] for row in cursor.fetchall()]
        #
        # cursor.execute("SELECT id_ticket FROM Tickets")
        # ticket_ids = [row['id_ticket'] for row in cursor.fetchall()]
        #
        # # Если таблица пустая, начинаем с id=1, иначе продолжаем существующую нумерацию
        # start_id = 1
        #
        # # Генерация данных
        # sales_data = []
        # num_records = 50  # Количество записей для генерации
        #
        # for i in range(start_id, start_id + num_records):
        #     sale_id = i
        #     user_id = random.choice(user_ids)
        #     ticket_id = random.choice(ticket_ids)
        #     count = random.randint(1, 5)  # От 1 до 5 билетов в одной продаже
        #
        #     # Дата продажи в пределах последнего года
        #     sale_date = fake.date_time_between(
        #         start_date='-1y',
        #         end_date='now'
        #     ).strftime('%Y-%m-%d %H:%M:%S')
        #
        #     sales_data.append((
        #         sale_id,
        #         user_id,
        #         ticket_id,
        #         count,
        #         sale_date
        #     ))
        #
        # # Вставка данных
        # insert_query = """
        #         INSERT INTO Sales (id_sale, id_user, id_ticket, count, sale_date)
        #         VALUES (%s, %s, %s, %s, %s)
        #         """
        # cursor.executemany(insert_query, sales_data)
        connection.commit()


finally:
    connection.close()