import sqlite3
import random
from elves import format_elf
from parameters import file_name, child_chance

conn = sqlite3.connect(f"{file_name}.db")
cursor = conn.cursor()

def start_pregnancies (married_women, year):
    pregnancies = []
    for woman in married_women:
        mother = format_elf(woman)
        spouse_id = mother.spouse_id
        cursor.execute("SELECT id, death_year FROM Elves WHERE id= :id", {"id": spouse_id})
        father = cursor.fetchone()
        # roll against child chance and check if father is still alive
        if random.randint(1, 100) <= child_chance and not father[1]:
            # create a pregnancy
            pregnancies.append({"current_year": year, "father_id": father[0], "parent_id": mother.id})
            pregnancies.append({"current_year": year, "father_id": None, "parent_id": father.id})
    cursor.executemany("UPDATE Elves SET last_child_conceived = :current_year, father_of_baby = :father_id WHERE id = :parent_id", pregnancies)
    conn.commit()     
    
