import sqlite3
import random
from elves import format_elf, new_elf

conn = sqlite3.connect("tolkien_elves.db")
cursor = conn.cursor()

# def find_relatives(target, year):
#     elf = format_elf(target)
#     cursor.execute('''
#         SELECT id, mother_id, father_id FROM Elves WHERE gender= "F" AND birth_year <= ? AND (death_year IS NULL OR death_year >= ?) AND (id= ? or id= ?)
#     ''', (year - 50, year, elf.mother_id, elf.father_id))
#     parents = cursor.fetchall()

def matchmake (unmarried_women, unmarried_men, year, marriage_chance = 40):
    for woman in unmarried_women:
        wife = format_elf(woman) 
        # find relatives
        if random.randint(1, 100) <= marriage_chance:
            relatives = ids_only(find_near_relatives(wife))
            cursor.execute('''
                SELECT * FROM Elves WHERE id NOT IN :relatives AND gender= "M" AND birth_year <= :birth_year AND (death_year IS NULL OR death_year >= :death_year) AND spouse_id IS NULL
            ''', {"relatives": relatives, "birth_year": year - 50, "death_year": year})
            unmarried_males = cursor.fetchall()
            preferred = []
            non_preferred = []
            for man in unmarried_males:
                pass

def ids_only (list):
    ids = []
    for line in list:
        ids.append(line[0])
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
            pregnancies.append((year, mother.id))
            pregnancies.append((year, father.id))
    cursor.executemany('''
        UPDATE Elves 
        SET last_child_conceived = ?
        WHERE id = ?
    ''', pregnancies)
    conn.commit()
        
def resolve_pregnancies (pregnant_women, year):
    babies = []
    for woman in pregnant_women:
        mother = format_elf(woman)
        spouse_id = mother.spouse_id
        cursor.execute('SELECT * FROM Elves WHERE id= :id', {"id": spouse_id})
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
        parent_ids = [{"id": woman.mother_id}, {"id": woman.father_id}]
        cursor.execute('SELECT id, mother_id, father_id FROM Elves WHERE id IN :parent_ids', {"parent_ids": parent_ids})
        parents = format_for_family_search(cursor.fetchmany())
        relatives += parents  
        # full siblings - shared children of both parents
        cursor.execute('SELECT id, mother_id, father_id FROM Elves WHERE mother_id= :mother_id AND father_id= :father_id', {"mother_id": parents[0].id, "father_id": parents[1].id})
        full_siblings = format_for_family_search(cursor.fetchmany())
        relatives += full_siblings
        # half siblings - children of one parent, but not the other
        cursor.execute('SELECT id, mother_id, father_id FROM Elves WHERE (mother_id= :mother_id AND NOT father_id= :father_id) OR (father_id= :father_id AND NOT mother_id= :mother_id)', {"mother_id": parents[0].id, "father_id": parents[1].id})
        half_siblings = format_for_family_search(cursor.fetchmany())
        relatives += half_siblings
    # children - search for anyone with id as mother id
    cursor.execute('SELECT id, mother_id, father_id FROM Elves WHERE mother_id= :mother_id', {"mother_id": woman.id})
    children = format_for_family_search(cursor.fetchmany())
    relatives += children
    if woman.generation not in (1, 2):
        # grandparents - parents of each parent
        grandparent_ids = []
        for parent in parents:
            grandparent_ids.append(parent.mother_id)
            grandparent_ids.append(parent.father_id)
        grandparent_ids = list(set(grandparent_ids))
        cursor.execute('SELECT id, mother_id, father_id FROM Elves WHERE id IN :grandparent_ids', {"grandparent_ids": grandparent_ids})
        grandparents = format_for_family_search(cursor.fetchmany())
        relatives += grandparents 
        # grandchildren - children of children
        if len(children) != 0:
            child_ids = map(lambda person: person.id, children)
            cursor.execute('SELECT id, mother_id, father_id FROM Elves WHERE mother_id IN :child_ids OR father_id IN child_ids', {"child_ids": child_ids})
            grandchildren = format_for_family_search(cursor.fetchmany())
            relatives += grandchildren
        # full aunt/uncle - children of both maternal grandparents or both paternal grandparents
        cursor.execute('SELECT id, mother_id, father_id FROM Elves WHERE (mother_id= :mat_grandma_id AND father_id= :mat_grandpa_id) OR (mother_id= :pat_grandma_id AND father_id= :pat_grandpa_id)', {"mat_grandma": grandparents[0].id, "mat_granpa": grandparents[1].id, "pat_grandma": grandparents[2].id, "pat_granpa": grandparents[3].id})
        full_piblings = format_for_family_search(cursor.fetchmany())
        relatives += full_piblings 
        # full niece/nephew - children of full siblings
        if len(full_siblings) != 0:
            full_sibling_ids = map(lambda person: person.id, full_siblings)
            cursor.execute('SELECT id, mother_id, father_id FROM Elves WHERE mother_id IN :full_sibling_ids OR father_id IN full_sibling_ids', {"full_sibling_ids": full_sibling_ids})
            full_niblings = format_for_family_search(cursor.fetchmany())
            relatives += full_niblings
        # half aunt/uncle - children of any grandparent
        cursor.execute('SELECT id, mother_id, father_id FROM Elves WHERE (mother_id= :mat_grandma_id AND NOT father_id= :mat_grandpa_id) OR (mother_id= :pat_grandma_id AND NOT father_id= :pat_grandpa_id) OR (father_id= :mat_grandpa_id AND NOT mother_id= :mat_grandma_id) OR (father_id= :pat_grandpa_id AND NOT mother_id= :pat_grandma_id)', {"mat_grandma": grandparents[0].id, "mat_granpa": grandparents[1].id, "pat_grandma": grandparents[2].id, "pat_granpa": grandparents[3].id})
        half_piblings = format_for_family_search(cursor.fetchmany())
        relatives += half_piblings
        # half niece/nephew - children of any half-siblings
        if len(half_siblings) != 0:
            half_sibling_ids = map(lambda person: person.id, half_siblings)
            cursor.execute('SELECT id, mother_id, father_id FROM Elves WHERE mother_id IN :half_sibling_ids OR father_id IN half_sibling_ids', {"half_sibling_ids": half_sibling_ids})
            half_niblings = format_for_family_search(cursor.fetchmany())
            relatives += half_niblings
        # full first cousin - children of full aunt/uncle
        if len(full_piblings) != 0:
            full_pibling_ids = map(lambda person: person.id, full_piblings)
            cursor.execute('SELECT id, mother_id, father_id FROM Elves WHERE mother_id IN :full_pibling_ids OR father_id IN full_pibling_ids', {"full_pibling_ids": full_pibling_ids})
            full_cousins = format_for_family_search(cursor.fetchmany())
            relatives += full_cousins
    return relatives