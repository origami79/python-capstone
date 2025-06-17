import sqlite3
import random
from parameters import file_name, death_divisor, adult_death_chance, child_death_chance, remarriage_possible

conn = sqlite3.connect(f"{file_name}.db")
cursor = conn.cursor()

def kill_population (adult_targets, child_targets, year):
    deaths = []
    spouses = []
    for adult in adult_targets:
        roll = random.randint(1, death_divisor)
        if roll <= adult_death_chance:
            deaths.append((year, adult[0]))
            if adult[7] is not None:
                spouses.append({"id": adult[7]})
    for child in child_targets:
        roll = random.randint(1, death_divisor)
        if roll <= child_death_chance:
            deaths.append((year, child[0]))
    cursor.executemany("UPDATE Elves  SET death_year = ? WHERE id = ?", deaths)
    conn.commit()

    if remarriage_possible and not len(spouses) == 0:
        cursor.executemany("UPDATE Elves SET spouse_id = NULL WHERE id = :id", spouses)
        conn.commit()
