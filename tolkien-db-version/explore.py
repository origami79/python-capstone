import sqlite3

conn = sqlite3.connect("tolkien_elves.db")
cursor = conn.cursor()


cursor.execute('SELECT * FROM Elves')
elves = cursor.fetchall()

for elf in elves:
    print(elf)

conn.close()