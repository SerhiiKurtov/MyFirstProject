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