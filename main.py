import sqlite3

import calendar

conn = sqlite3.connect('salon.sqlite')
cur = conn.cursor()

cur.execute('''
CREATE TABLE IF NOT EXISTS "Client" (
    "id" INTEGER PRIMARY KEY AUTOINCREMENT NOT NULL,
    "name" TEXT NOT NULL,
    "phone" TEXT NOT NULL
);
''')
conn.commit()

cur.execute('''
CREATE TABLE IF NOT EXISTS "Procedure" (
    "id" INTEGER PRIMARY KEY AUTOINCREMENT NOT NULL,
    "title" TEXT NOT NULL,
    "price" INTEGER
);
''')
conn.commit()

cur.execute('''
CREATE TABLE IF NOT EXISTS "Schedule" (
    "id" INTEGER PRIMARY KEY AUTOINCREMENT,
    "work_date" TEXT NOT NULL,
    "work_time" TEXT NOT NULL,
    "is_available" INTEGER DEFAULT 1
);
''')
conn.commit()

cur.execute('''
CREATE TABLE IF NOT EXISTS "Bookings" (
    "status" TEXT DEFAULT 'pending',
    "id" INTEGER PRIMARY KEY AUTOINCREMENT NOT NULL,
    "client_id" INTEGER,
    "procedure_id" INTEGER,
    "full_time" TEXT NOT NULL, -- Формат: 'YYYY-MM-DD HH:MM'
    FOREIGN KEY ("client_id") REFERENCES "Client" ("id"),
    FOREIGN KEY ("procedure_id") REFERENCES "Procedure" ("id")
);
''')
conn.commit()

cur.execute('''
CREATE UNIQUE INDEX IF NOT EXISTS idx_date_time ON Schedule (work_date, work_time);
''')
conn.commit()

def add_procedures(cur, conn) :
    while True :
        services = input("Введіть назву процедури, для завершення введіть стоп: ").strip()
        if services.lower() == 'стоп' :
            print("Процедури збережені!")
            break
        services_price = input(f"Ввудіть ціну процедури {services}: ").strip()
        try :
            cur.execute("INSERT INTO Procedure (title, price) VALUES (?, ?)", (services, services_price))
            print(f"{services} - {services_price} грн збережено!")
        except Exception as e :
            print(f"Виникла помилка: {e}")
    conn.commit()

#add_procedures(cur, conn)

def setup_schedule(cur, conn) :

    try :
        year = int(input("Виберіть рік (наприклад 2026): ").strip())
        month = int(input("Виберіть місяць від 1 до 12: ").strip())
    except Exception as e :
        print(f"Виникла помилка: {e}, введіть данні цифрами!")
        return

    num_day = calendar.monthrange(year, month)[1]

    time_day = []
    while True :
        hour = input("Введіть час прийому, для завершення введіть стоп: ").strip()
        if hour.lower() == 'стоп' :
            print("Робоці години визначені!")
            break
        time_day.append(hour)

    for day in range(1, num_day + 1) :
        current_data = f"{year}-{month:02}-{day:02}"
        for hour in time_day :
            try :
                cur.execute("INSERT INTO Schedule (work_date, work_time) VALUES (?, ?)", (current_data, hour))
            except sqlite3.IntegrityError :
                print(f"Помилка: Час {hour} на цю дату вже існує!")
            except Exception as e :
                print(f"Виникла помилка: {e}")
    conn.commit()

    weekend_input = input("Введіть числа місяця, які будуть вихідними (через пробіл): ").strip().split()
    for day_off in weekend_input :
        weekends = f"{year}-{month:02}-{int(day_off):02}"
        cur.execute("UPDATE Schedule SET is_available = 2 WHERE work_date = ?", (weekends,))
        print(f"Вихідні: {weekends}")
    conn.commit()

#setup_schedule(cur, conn)

def records(cur, conn) :
    cur.execute('''
        SELECT Bookings.id, Client.name, Bookings.full_time
        FROM Bookings JOIN Client
        ON Bookings.client_id = Client.id
    ''')
    rows = cur.fetchall()
    if not rows :
        print("Записів поки немає.")
    else :
        for row in rows :
            print(f"ID: {row[0]:<3} | Клієнт: {row[1]:<30} | Час: {row[2]}")

    cancel_id = input("Введіть ID запису для СКАСУВАННЯ (або натисніть Enter, щоб вийти) :").strip()
    if cancel_id :
        cur.execute("SELECT full_time FROM Bookings WHERE id = ?", (cancel_id,))
        result = cur.fetchone()
        if result :
            booked_time = result[0]
            date_part, time_part = booked_time.split()
            cur.execute("UPDATE Schedule SET is_available = 1 WHERE work_date = ? AND work_time = ?", (date_part, time_part))
            cur.execute("DELETE FROM Bookings WHERE id = ?", (cancel_id,))
            conn.commit()
            print("Запис успішно скасовано, час знову вільний!")
        else :
            print("Запис з таким ID не знайдено.")
    conn.commit()

#records(cur, conn)

def client_booking(cur, conn) :
    cur.execute("SELECT id, title, price FROM Procedure")
    rows = cur.fetchall()
    if not rows :
        print("Послуги не існує.")
    else :
        for row in rows :
            print(f"ID: {row[0]:<3} | Процедура: {row[1]:<30} | Ціна: {row[2]}")

    valid_ids = [row[0] for row in rows]
    try :
        services = int(input("Оберіть номер бажаної процедури: ").strip())
    except :
        print("Введіть значення цифрою")
        return
    if services in valid_ids :
        cur.execute("SELECT id, work_date, work_time FROM Schedule WHERE is_available = 1")
        data = cur.fetchall()
        if not data :
            print("Дати не існує.")
        else :
            for date in data :
                print(f"ID: {date[0]:<3} | Дата: {date[1]:<15} | Час: {date[2]}")
    else :
        return
    try :
        date_service = int(input("Оберіть номер бажаного часу: ").strip())
    except :
        print("Введіть значення цифрою")
        return
    cur.execute("SELECT work_date, work_time FROM Schedule WHERE id = ?", (date_service,))
    res = cur.fetchone()
    if not res :
        print("Такий час не знайдено!")
        return
    selected_time = f"{res[0]} {res[1]}"

    while True :
        name = input("Введіть ваше ім'я та прізвище: ").strip()
        if " " in name and len(name) >= 5 :
            break
        else :
            print("Помилка: введіть, будь ласка, і ім'я, і прізвище!")

    while True :
        phone = input("Введіть номер телефону: ").strip()
        if phone.isdigit() and len(phone) == 10 :
            print("Дякуємо! Номер прийнято.")
            break
        else :
            print("Введіть коретний номер телефону!")
    conn.commit()

    #client_booking(cur, conn)

    cur.execute("INSERT INTO Client (name, phone) VALUES (?, ?)", (name, phone))
    client_id = cur.lastrowid
    cur.execute("INSERT INTO Bookings (client_id, procedure_id, full_time) VALUES (?, ?, ?)", (client_id, services, selected_time))
    cur.execute("UPDATE Schedule SET is_available = 0 WHERE id = ?", (date_service,))
    conn.commit()
    print(f"Запис успішно створено! Чекаємо на вас {selected_time}")

def confirm_booking(cur, conn) :
    cur.execute('''
        SELECT Bookings.id, Bookings.status, Client.name, Procedure.title, Bookings.full_time
        FROM Bookings
        JOIN Client ON Bookings.client_id = Client.id
        JOIN Procedure ON Bookings.procedure_id = Procedure.id
        WHERE Bookings.status = 'pending'
        ''')
    rows = cur.fetchall()
    if not rows :
        print("Запису не існує")
    else :
        for row in rows :
                print(f"ID: {row[0]:<3} | Статус: {row[1]:<30} | Клієнт: {row[2]:<30} | Процедура: {row[3]:<30} | Дата: {row[4]:<30}")

    while True :
        confirm = input("Виберіть ID для підтвердження(стоп для завершення):").strip()
        if confirm.lower() == 'стоп' :
            print("Допобачення")
            break
        elif confirm.isdigit() :
            cur.execute("UPDATE Bookings SET status = ? WHERE id = ?", ('confirmed', confirm))
            print(f"Запис №{confirm} підтверджено!")
        else :
            print("Введіть коректне ID")
    conn.commit()

#confirm_booking(cur, conn)