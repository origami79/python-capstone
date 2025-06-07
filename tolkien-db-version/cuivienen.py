import sqlite3
from elves import new_elf
from years import matchmake, start_pregnancies, resolve_pregnancies, kill_population

conn = sqlite3.connect("tolkien_elves.db")
cursor = conn.cursor()

cursor.execute('''
    DROP TABLE Elves
''')
cursor.execute('''
    DROP TABLE Relationships
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
        last_child_conceived INTEGER,
        father_of_baby INTEGER               
    )
''')
cursor.execute('''
    CREATE TABLE IF NOT EXISTS Relationships (
        id INTEGER PRIMARY KEY,
        base_id INT NOT NULL,
        relation_id INT NOT NULL,
        relationship STR NOT NULL,
        FOREIGN KEY (base_id) REFERENCES Elves(id),
        FOREIGN KEY (relation_id) REFERENCES Elves(id)              
    )
''')
conn.commit()

for i in range(144):
    if i % 2 == 0:
        elf = new_elf(birth_year = -50, generation= 1, gender= "M", spouse_id= i+2)
        relation = {"base_id": i+1, "relation_id": i+2, "relationship": "spouse"}
    else:
        elf = new_elf(birth_year = -50, generation= 1, gender= "F", spouse_id= i)
        relation = {"base_id": i+1, "relation_id": i, "relationship": "spouse"}
    cursor.execute('''
        INSERT INTO Elves (birth_year, generation, target_children, gender, spouse_id, target_children, first_child_year) 
        VALUES (:birth_year, :generation, :target_children, :gender, :spouse_id, :target_children, :first_child_year)
    ''', elf)
    cursor.execute('''
        INSERT INTO Relationships (base_id, relation_id, relationship) VALUES (:base_id, :relation_id, :relationship)
    ''', relation)
    conn.commit()

def simulate_year(year):
    # matchmake unmarried
    cursor.execute('''
        SELECT * FROM Elves WHERE gender= "F" AND birth_year <= ? AND (death_year IS NULL OR death_year >= ?) AND spouse_id IS NULL AND first_child_year IS NOT NULL
    ''', (year - 50, year))
    unmarried_females = cursor.fetchall()
    matchmake(unmarried_females, year)
    # start new pregnancies
    cursor.execute('''
        SELECT * FROM Elves WHERE gender= "F" AND birth_year <= ? AND spouse_id IS NOT NULL AND (death_year IS NULL OR death_year >= ?) AND ((first_child_year >= ? AND last_child_conceived IS NULL) OR (last_child_conceived <= ?))
    ''', (year - 50, year, year, year - 20))
    women_ready_for_a_child = cursor.fetchall()
    start_pregnancies(women_ready_for_a_child, year)
    # finish existing pregnancies
    cursor.execute('''
        SELECT * FROM Elves WHERE gender= "F" AND birth_year <= ? AND (death_year IS NULL OR death_year >= ?) AND last_child_conceived = ?
    ''', (year - 50, year, year - 10))
    women_ready_for_birth = cursor.fetchall()
    resolve_pregnancies(women_ready_for_birth, year)
    # kill random population
    # search for adult men and adult women who are not pregnant
    cursor.execute('''
        SELECT * FROM Elves WHERE (gender= "M" AND birth_year <= :birth_year AND death_year IS NULL) OR 
            (gender= "F" AND birth_year <= :birth_year AND death_year IS NULL AND ((first_child_year >= year AND last_child_conceived IS NULL) OR (last_child_conceived >= :last_conception)))
    ''', {"birth_year": year - 50, "year": year, "last_conception": year - 20})
    adults = cursor.fetchall()  
    # search for children
    cursor.execute('''
        SELECT * FROM Elves WHERE birth_year BETWEEN ? AND ? AND death_year IS NULL
    ''', (year - 50, year - 5))
    children = cursor.fetchall()
    kill_population(adults, children, year)

# for i in range(600):
#     simulate_year(i) 

# cursor.execute('SELECT * FROM Elves')
# elves = cursor.fetchall()

# for elf in elves:
#     print(elf)

conn.close()

print("All done <3")

