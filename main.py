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
