import sqlite3
import random
from parameters import file_name

conn = sqlite3.connect(f"{file_name}.db")
cursor = conn.cursor()

def kill_population (adult_targets, child_targets, year, death_chance = 50000):
    deaths = []
    spouses = []
    for adult in adult_targets:
        roll = random.randint(1, death_chance)
        if roll <= 2:
            deaths.append((year, adult[0]))
            if adult[7] is not None:
                spouses.append({"id": adult[7]})
    for child in child_targets:
        roll = random.randint(1, death_chance)
        if roll <= 1:
            deaths.append((year, child[0]))
    cursor.executemany('''
        UPDATE Elves 
        SET death_year = ?
        WHERE id = ?
    ''', deaths)
    conn.commit()

    if not len(spouses) == 0:
        cursor.executemany('''
            UPDATE Elves 
            SET spouse_id = NULL
            WHERE id = :id
        ''', spouses)
        conn.commit()
