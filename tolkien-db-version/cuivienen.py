import sqlite3
from elves import new_elf

conn = sqlite3.connect("tolkien_elves.db")
cursor = conn.cursor()

cursor.execute('''
    DROP TABLE Elves
''')
conn.commit()

cursor.execute('''
    CREATE TABLE IF NOT EXISTS Elves (
        id INTEGER PRIMARY KEY,
        mother_id INTEGER,
        father_id INTEGER,
        birth_year INTEGER NOT NULL,
        death_year INTEGER,
        generation INTEGER NOT NULL,
        gender STR,
        spouse_id INTEGER,
        target_children INTEGER NOT NULL,
        first_child_year INTEGER,
        last_child_concieved INTEGER,
               
        FOREIGN KEY (mother_id) REFERENCES Elves(id),
        FOREIGN KEY (father_id) REFERENCES Elves(id),
        FOREIGN KEY (spouse_id) REFERENCES Elves(id)
    )
''')
conn.commit()

for i in range(14):
    if i % 2 == 0:
        elf = new_elf(birth_year = -50, generation= 1, gender= "M", spouse_id= i+2)
    else:
        elf = new_elf(birth_year = -50, generation= 1, gender= "F", spouse_id= i)
    cursor.execute('''
        INSERT INTO Elves (birth_year, generation, target_children, gender, spouse_id) 
        VALUES (:birth_year, :generation, :target_children, :gender, :spouse_id)
    ''', elf)
    conn.commit()
    
cursor.execute('SELECT * FROM Elves')
elves = cursor.fetchall()

for elf in elves:
    print(elf)
