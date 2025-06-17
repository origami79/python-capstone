import sqlite3
from elves import new_elf
from pregnancy import start_pregnancies
from deaths import kill_population
from matchmaking import matchmake
from birth import resolve_pregnancies
from parameters import file_name, starting_population, adulthood, pregnancy, time_between_children, infant_immortality, start_year, end_year

import time
total_start = time.time()

conn = sqlite3.connect(f"{file_name}.db")
cursor = conn.cursor()

cursor.execute('''
    DROP TABLE IF EXISTS Elves
''')
cursor.execute('''
    DROP TABLE IF EXISTS Relationships
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
        current_children INTEGER NOT NULL,
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
cursor.execute('''
    CREATE INDEX index_relationship_base_id ON Relationships(base_id);
''')
conn.commit()

for i in range(starting_population):
    if i % 2 == 0:
        elf = new_elf(birth_year = 0 - adulthood, generation= 1, gender= "M", spouse_id= i+2)
        relation = {"base_id": i+1, "relation_id": i+2, "relationship": "spouse"}
    else:
        elf = new_elf(birth_year = 0 - adulthood, generation= 1, gender= "F", spouse_id= i)
        relation = {"base_id": i+1, "relation_id": i, "relationship": "spouse"}
    cursor.execute('''
        INSERT INTO Elves (id, mother_id, father_id, birth_year, death_year, generation, gender, spouse_id, target_children, current_children, first_child_year, last_child_conceived, father_of_baby) 
        VALUES (NULL, :mother_id, :father_id, :birth_year, :death_year, :generation, :gender, :spouse_id, :target_children, :current_children, :first_child_year, :last_child_conceived, :father_of_baby)
    ''', elf)
    cursor.execute('''
        INSERT INTO Relationships (base_id, relation_id, relationship) VALUES (:base_id, :relation_id, :relationship)
    ''', relation)
    conn.commit()

def simulate_year(year):
    # matchmake unmarried
    cursor.execute('''
        SELECT * FROM Elves WHERE gender= "F" AND birth_year <= :birth_year_for_adult AND death_year IS NULL AND spouse_id IS NULL AND first_child_year IS NOT NULL
    ''', {"birth_year_for_adult": year - adulthood})
    unmarried_females = cursor.fetchall()
    matchmake(unmarried_females, year)
    # start new pregnancies
    cursor.execute('''
        SELECT * FROM Elves WHERE gender= "F" AND current_children < target_children AND birth_year <= :birth_year_for_adult AND spouse_id IS NOT NULL AND death_year IS NULL AND ((first_child_year <= :current_year AND last_child_conceived IS NULL) OR (last_child_conceived <= :year_if_ready_for_new_child))
    ''', {"birth_year_for_adult": year - adulthood, "current_year": year, "year_if_ready_for_new_child": year - (pregnancy + time_between_children)})
    women_ready_for_a_child = cursor.fetchall()
    start_pregnancies(women_ready_for_a_child, year)
    # finish existing pregnancies
    cursor.execute('''
        SELECT * FROM Elves WHERE gender= "F" AND birth_year <= :birth_year_for_adult AND death_year IS NULL AND last_child_conceived = :year_if_ready_for_birth
    ''', {"birth_year_for_adult": year - adulthood, "year_if_ready_for_birth": year - pregnancy})
    women_ready_for_birth = cursor.fetchall()
    resolve_pregnancies(women_ready_for_birth, year)
    # kill random population
    # search for adult men and adult women who are not pregnant
    cursor.execute('''
        SELECT * FROM Elves WHERE (gender= "M" AND birth_year <= :year_for_adult AND death_year IS NULL) OR (gender= "F" AND birth_year <= :year_for_adult AND (death_year IS NULL OR death_year <= :year) AND (last_child_conceived IS NULL OR last_child_conceived <= :long_enough_since_conception OR last_child_conceived > :year))
    ''', {"year_for_adult": year - adulthood, "year": year, "long_enough_since_conception": year - (pregnancy + time_between_children)})
    adults = cursor.fetchall()  
    # search for children
    cursor.execute('''
        SELECT * FROM Elves WHERE birth_year BETWEEN :year_for_adult AND :year_out_of_infancy AND death_year IS NULL
    ''', {"year_for_adult": year - adulthood, "year_out_of_infancy": year - infant_immortality})
    children = cursor.fetchall()
    kill_population(adults, children, year)

for i in range(start_year, end_year):
    simulate_year(i)


conn.close()
total_end = time.time()


print("All done <3")
print("Total Time Taken:", int((total_end-total_start)/60), "minutes and", int((total_end-total_start) % 60), "seconds")

