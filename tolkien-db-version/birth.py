from elves import format_elf, new_elf
import sqlite3

conn = sqlite3.connect("tolkien_elves.db")
cursor = conn.cursor()

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
    update_all_relationships(year)

lookup = {
    "parent": "grandparent",
    "grandparent": "great_grandparent",
    "great_grandparent": None,
    "full_sibling": "full_pibling",
    "half_sibling": "half_pibling",
    "full_pibling": "full_great_pibling",
    "full_great_pibling": None,
    "half_pibling": None,
    "full_nibling": "full_first_cousin",
    "half_nibling": None,
    "full_first_cousin": None,
    "child": "sibling-sort",
    "grandchild": "nibling-sort",
    "spouse": None
}

def format_elves(data):
    formated = []
    for line in data:
        formated.append({"id": line[0], "mother_id": line[1], "father_id": line[2]})
    return formated

def update_all_relationships (year):
    relationships = []
    cursor.execute("SELECT id, mother_id, father_id FROM Elves WHERE birth_year= :year", {"year": year})
    babies = format_elves(cursor.fetchall())
    for baby in babies:
        relationships += update_relationships(baby)
    cursor.executemany("INSERT INTO Relationships (base_id, relation_id, relationship) VALUES (:base_id, :relation_id, :relationship)", relationships)
    conn.commit()

def update_relationships (elfling):
    cursor.execute("Select relation_id, relationship FROM Relationships WHERE base_id IN (?, ?)", [elfling["mother_id"], elfling["father_id"]])
    relatives = cursor.fetchall()

    relative_updates = [{"base_id": elfling["id"], "relation_id": elfling["mother_id"], "relationship": "parent"}, {"base_id": elfling["id"], "relation_id": elfling["father_id"], "relationship": "parent"}, {"base_id": elfling["mother_id"], "relation_id": elfling["id"], "relationship": "child"}, {"base_id": elfling["father_id"], "relation_id": elfling["id"], "relationship": "child"}]
    siblings = []
    niblings = []
    for relative in relatives:
        new_relation = lookup[relative[1]] 
        if new_relation == "sibling-sort":
            siblings.append(relative[0])
        elif new_relation == "nibling-sort":
            niblings.append(relative[0])
        else:
            if new_relation is not None:
                relative_updates.append({"base_id": elfling["id"], "relation_id": relative[0], "relationship": new_relation})
                relative_updates.append({"base_id": relative[0], "relation_id": elfling["id"], "relationship": new_relation})
    
    while len(siblings) > 0:
        current = siblings.pop()
        if current in siblings:
            relative_updates.append({"base_id": elfling["id"], "relation_id": current, "relationship": "full_sibling"})
            relative_updates.append({"base_id": current, "relation_id": elfling["id"], "relationship": "full_sibling"})
            siblings.remove(current)
        else:
            relative_updates.append({"base_id": elfling["id"], "relation_id": current, "relationship": "half_sibling"})
            relative_updates.append({"base_id": current, "relation_id": elfling["id"], "relationship": "half_sibling"})

    for nibling in niblings:
        cursor.execute("SELECT relation_id FROM Relationships WHERE base_id= :base_id AND relationship= :relationship", {"base_id": nibling, "relationship": "grandparent"})
        grandparents = cursor.fetchall()
        if elfling["mother_id"] in grandparents and elfling["father_id"] in grandparents:
            relative_updates.append({"base_id": elfling["id"], "relation_id": nibling, "relationship": "full_nibling"})
            relative_updates.append({"base_id": nibling, "relation_id": elfling["id"], "relationship": "full_nibling"})
        else:
            relative_updates.append({"base_id": elfling["id"], "relation_id": nibling, "relationship": "half_nibling"})
            relative_updates.append({"base_id": nibling, "relation_id": elfling["id"], "relationship": "half_nibling"})
    return relative_updates