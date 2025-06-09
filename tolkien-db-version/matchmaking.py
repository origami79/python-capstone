import random
from elves import format_elf
import sqlite3

conn = sqlite3.connect("tolkien_elves.db")
cursor = conn.cursor()

def matchmake (unmarried_women, year, marriage_chance = 40):
    for woman in unmarried_women:
        wife = format_elf(woman) 
        # find relatives
        if random.randint(1, 100) <= marriage_chance:
            query = "SELECT relation_id FROM Relationships WHERE base_id= :base_id"
            cursor.execute(query, {"base_id": wife.id})
            relatives = list(map(lambda tuple: tuple[0], cursor.fetchall()))
            query = "SELECT * FROM Elves WHERE gender= 'M' AND birth_year <= ? AND (death_year IS NULL OR death_year >= ?) AND spouse_id IS NULL AND id NOT IN ({}) AND first_child_year IS NOT NULL".format(','.join('?' * len(relatives)))
            cursor.execute(query, [year - 50, year, *relatives])
            unmarried_males = cursor.fetchall()
            best_match = []
            okay_match = []
            poor_match = []
            for male in unmarried_males:
                man = format_elf(male)
                if abs(man.target_children - wife.target_children) <= 1 and abs(man.first_child_year - wife.first_child_year) <= 10:
                    best_match.append(man.id)
                elif abs(man.target_children - wife.target_children) <= 1 or abs(man.first_child_year - wife.first_child_year) <= 10:
                    okay_match.append(man.id)
                else:
                    poor_match.append(man.id)
            # limit the pool a bit to avoid infinite chances
            match_found = False
            best_suitors = list(set(random.choices(best_match, k= min(10, len(best_match)))))
            okay_suitors = list(set(random.choices(okay_match, k= min(10, len(okay_match)))))
            poor_suitors = list(set(random.choices(poor_match, k= min(10, len(poor_match)))))
            for man_id in best_suitors:
                if random.randint(1, 100) <= 20:
                    create_marriage(wife.id, man_id)
                    match_found = True
                    break
            if not match_found:
                for man_id in okay_suitors:
                    if random.randint(1, 100) <= 10:
                        create_marriage(wife.id, man_id)
                        match_found = True
                        break
            if not match_found:
                for man_id in poor_suitors:
                    if random.randint(1, 100) <= 10:
                        create_marriage(wife.id, man_id)
                        match_found = True
                        break

def format_for_family_search(data):
    formated = []
    for line in data:
        formated.append({"id": line[0], "mother_id": line[1], "father_id": line[2]})
    return formated

def create_marriage(wife_id, husband_id):
    cursor.execute("UPDATE Elves SET spouse_id = :spouse_id WHERE id = :id", {"spouse_id": wife_id, "id": husband_id})
    cursor.execute("UPDATE Elves SET spouse_id = :spouse_id WHERE id = :id", {"spouse_id": husband_id, "id": wife_id})
    cursor.execute("INSERT INTO Relationships (base_id, relation_id, relationship) VALUES (:base_id, :relation_id, :relationship)", {"base_id": wife_id, "relation_id": husband_id, "relationship": "spouse"})
    cursor.execute("INSERT INTO Relationships (base_id, relation_id, relationship) VALUES (:base_id, :relation_id, :relationship)", {"base_id": husband_id, "relation_id": wife_id, "relationship": "spouse"})
    conn.commit()
