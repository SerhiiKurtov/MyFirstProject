import sqlite3

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