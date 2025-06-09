import sqlite3
import random
from elves import format_elf

conn = sqlite3.connect("tolkien_elves_600_revised.db")
cursor = conn.cursor()

def ids_only (list):
    ids = []
    for line in list:
        ids.append(line["id"])
    return ids

def start_pregnancies (married_women, year, child_chance = 40):
    pregnancies = []
    for woman in married_women:
        mother = format_elf(woman)
        spouse_id = mother.spouse_id
        cursor.execute('SELECT id, death_year FROM Elves WHERE id= :id', {"id": spouse_id})
        father = cursor.fetchone()

        # roll against child chance if father still alive
        if random.randint(1, 100) <= child_chance and not father[1]:
            # create a pregnancy
            pregnancies.append((year, father[0], mother.id))
            pregnancies.append((year, None, father[0]))
    cursor.executemany('''
        UPDATE Elves 
        SET last_child_conceived = ?, father_of_baby = ?
        WHERE id = ?
    ''', pregnancies)
    conn.commit()     
    
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
