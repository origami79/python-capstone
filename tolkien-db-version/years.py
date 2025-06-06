import sqlite3
import random
from elves import format_elf, new_elf

conn = sqlite3.connect("tolkien_elves.db")
cursor = conn.cursor()

def matchmake (unmarried_women, year, marriage_chance = 40):
    for woman in unmarried_women:
        wife = format_elf(woman) 
        # find relatives
        if random.randint(1, 100) <= marriage_chance:
            relatives = ids_only(find_near_relatives(wife))
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

def create_marriage(wife_id, husband_id):
    cursor.execute("UPDATE Elves SET spouse_id = :spouse_id WHERE id = :id", {"spouse_id": wife_id, "id": husband_id})
    cursor.execute("UPDATE Elves SET spouse_id = :spouse_id WHERE id = :id", {"spouse_id": husband_id, "id": wife_id})
    conn.commit()

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
        cursor.execute('SELECT * FROM Elves WHERE id= :id', {"id": spouse_id})
        father = format_elf(cursor.fetchone())
        # roll against child chance
        if random.randint(1, 100) <= child_chance:
            # create a pregnancy
            pregnancies.append((year, father.id, mother.id))
            pregnancies.append((year, None, father.id))
    cursor.executemany('''
        UPDATE Elves 
        SET last_child_conceived = ?, father_of_baby = ?
        WHERE id = ?
    ''', pregnancies)
    conn.commit()
        
def resolve_pregnancies (pregnant_women, year):
    babies = []
    for woman in pregnant_women:
        mother = format_elf(woman)
        father_id = mother.father_of_baby
        cursor.execute('SELECT * FROM Elves WHERE id= :id', {"id": father_id})
        father = format_elf(cursor.fetchone())
        generation = max([father.generation, mother.generation]) + 1
        child = new_elf(year, generation, mother.id, father.id)
        babies.append(child)
    cursor.executemany('''
        INSERT INTO Elves (mother_id, father_id, birth_year, generation, target_children, gender, spouse_id, target_children, first_child_year) 
        VALUES (:mother_id, :father_id, :birth_year, :generation, :target_children, :gender, :spouse_id, :target_children, :first_child_year)
    ''', babies)
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

def format_for_family_search(data):
    formated = []
    for line in data:
        formated.append({"id": line[0], "mother_id": line[1], "father_id": line[2]})
    return formated

def find_near_relatives (woman):
    relatives = []
    # parents - check mother id and father id
    if woman.generation != 1:
        parent_ids = [woman.mother_id, woman.father_id]
        query = "SELECT id, mother_id, father_id FROM Elves WHERE id IN ({})".format(','.join('?' * len(parent_ids)))
        cursor.execute(query, parent_ids)
        parents = format_for_family_search(cursor.fetchall())
        relatives += parents  
        # full siblings - shared children of both parents
        cursor.execute('SELECT id, mother_id, father_id FROM Elves WHERE mother_id= :mother_id AND father_id= :father_id', {"mother_id": parents[0]["id"], "father_id": parents[1]["id"]})
        full_siblings = format_for_family_search(cursor.fetchall())
        relatives += full_siblings
        # half siblings - children of one parent, but not the other
        cursor.execute('SELECT id, mother_id, father_id FROM Elves WHERE (mother_id= :mother_id AND NOT father_id= :father_id) OR (father_id= :father_id AND NOT mother_id= :mother_id)', {"mother_id": parents[0]["id"], "father_id": parents[1]["id"]})
        half_siblings = format_for_family_search(cursor.fetchall())
        relatives += half_siblings
    # children - search for anyone with id as mother id
    cursor.execute('SELECT id, mother_id, father_id FROM Elves WHERE mother_id= :mother_id', {"mother_id": woman.id})
    children = format_for_family_search(cursor.fetchall())
    relatives += children
    if woman.generation not in (1, 2):
        # grandparents - parents of each parent
        grandparent_ids = []
        for parent in parents:
            grandparent_ids.append(parent["mother_id"])
            grandparent_ids.append(parent["father_id"])
        grandparent_ids = list(set(grandparent_ids))
        query = 'SELECT id, mother_id, father_id FROM Elves WHERE id IN ({})'.format(','.join('?' * len(grandparent_ids)))
        cursor.execute(query, grandparent_ids)
        grandparents = format_for_family_search(cursor.fetchall())
        relatives += grandparents 
        # grandchildren - children of children
        if len(children) != 0:
            child_ids = list(map(lambda person: person["id"], children))
            query = 'SELECT id, mother_id, father_id FROM Elves WHERE mother_id IN ({}) OR father_id IN ({})'.format(','.join('?' * len(child_ids)),','.join('?' * len(child_ids)))
            cursor.execute(query, child_ids + child_ids)
            grandchildren = format_for_family_search(cursor.fetchall())
            relatives += grandchildren
        # full aunt/uncle - children of both maternal grandparents or both paternal grandparents
        if len(grandparents) == 2:
            cursor.execute('SELECT id, mother_id, father_id FROM Elves WHERE (mother_id= :grandma_id AND father_id= :grandpa_id)', {"grandma_id": grandparents[0]["id"], "grandpa_id": grandparents[1]["id"]})
            full_piblings = format_for_family_search(cursor.fetchall())
            relatives += full_piblings 
        else:
            cursor.execute('SELECT id, mother_id, father_id FROM Elves WHERE (mother_id= :mat_grandma_id AND father_id= :mat_grandpa_id) OR (mother_id= :pat_grandma_id AND father_id= :pat_grandpa_id)', {"mat_grandma_id": grandparents[0]["id"], "mat_grandpa_id": grandparents[1]["id"], "pat_grandma_id": grandparents[2]["id"], "pat_grandpa_id": grandparents[3]["id"]})
            full_piblings = format_for_family_search(cursor.fetchall())
            relatives += full_piblings 
        # full niece/nephew - children of full siblings
        if len(full_siblings) != 0:
            full_sibling_ids = list(map(lambda person: person["id"], full_siblings))
            query = 'SELECT id, mother_id, father_id FROM Elves WHERE mother_id IN ({}) OR father_id IN ({})'.format(','.join('?' * len(full_sibling_ids)), ','.join('?' * len(full_sibling_ids)))
            cursor.execute(query, full_sibling_ids + full_sibling_ids)
            full_niblings = format_for_family_search(cursor.fetchall())
            relatives += full_niblings
        # half aunt/uncle - children of any grandparent
        if len(grandparents) == 2:
            cursor.execute('SELECT id, mother_id, father_id FROM Elves WHERE (mother_id= :grandma_id AND NOT father_id= :grandpa_id) OR (father_id= :grandpa_id AND NOT mother_id= :grandma_id)', {"grandma_id": grandparents[0]["id"], "grandpa_id": grandparents[1]["id"]})
            half_piblings = format_for_family_search(cursor.fetchall())
            relatives += half_piblings 
        else:
            cursor.execute('SELECT id, mother_id, father_id FROM Elves WHERE (mother_id= :mat_grandma_id AND NOT father_id= :mat_grandpa_id) OR (mother_id= :pat_grandma_id AND NOT father_id= :pat_grandpa_id) OR (father_id= :mat_grandpa_id AND NOT mother_id= :mat_grandma_id) OR (father_id= :pat_grandpa_id AND NOT mother_id= :pat_grandma_id)', {"mat_grandma_id": grandparents[0]["id"], "mat_grandpa_id": grandparents[1]["id"], "pat_grandma_id": grandparents[2]["id"], "pat_grandpa_id": grandparents[3]["id"]})
            half_piblings = format_for_family_search(cursor.fetchall())
            relatives += half_piblings
        # half niece/nephew - children of any half-siblings
        if len(half_siblings) != 0:
            half_sibling_ids = list(map(lambda person: person["id"], half_siblings))
            query = 'SELECT id, mother_id, father_id FROM Elves WHERE mother_id IN ({}) OR father_id IN ({})'.format(','.join('?' * len(half_sibling_ids)), ','.join('?' * len(half_sibling_ids)))
            cursor.execute(query, half_sibling_ids + half_sibling_ids)
            half_niblings = format_for_family_search(cursor.fetchall())
            relatives += half_niblings
        # full first cousin - children of full aunt/uncle
        if len(full_piblings) != 0:
            full_pibling_ids = list(map(lambda person: person["id"], full_piblings))
            query = 'SELECT id, mother_id, father_id FROM Elves WHERE mother_id IN ({}) OR father_id IN ({})'.format(','.join('?' * len(full_pibling_ids)), ','.join('?' * len(full_pibling_ids)))
            cursor.execute(query, full_pibling_ids + full_pibling_ids)
            full_cousins = format_for_family_search(cursor.fetchall())
            relatives += full_cousins
    return relatives