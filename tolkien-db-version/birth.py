from elves import format_elf, new_elf
import sqlite3

conn = sqlite3.connect("tolkien_elves_600_revised.db")
cursor = conn.cursor()

def resolve_pregnancies (pregnant_women, year):
    babies = []
    parents = []
    for woman in pregnant_women:
        mother = format_elf(woman)
        father_id = mother.father_of_baby
        cursor.execute('SELECT * FROM Elves WHERE id= :id', {"id": father_id})
        father = format_elf(cursor.fetchone())
        generation = max([father.generation, mother.generation]) + 1
        child = new_elf(year, generation, mother.id, father.id)
        babies.append(child)
        parents += [{"current_children": mother.current_children + 1, "id": mother.id}, {"current_children": father.current_children + 1, "id": father.id}]
    cursor.executemany('''
        INSERT INTO Elves (id, mother_id, father_id, birth_year, death_year, generation, gender, spouse_id, target_children, current_children, first_child_year, last_child_conceived, father_of_baby) 
        VALUES (NULL, :mother_id, :father_id, :birth_year, :death_year, :generation, :gender, :spouse_id, :target_children, :current_children, :first_child_year, :last_child_conceived, :father_of_baby)
    ''', babies)
    conn.commit()
    cursor.executemany("UPDATE Elves SET current_children = :current_children WHERE id = :id", parents)
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
    "great_grandchild": "great-nibling-sort",
    "spouse": None
}

reverse_lookup = {
    "parent": "grandchild",
    "grandparent": "great_grandchild",
    "great_grandparent": None,
    "full_sibling": "full_nibling",
    "half_sibling": "half_nibling",
    "full_pibling": "full_great_nibling",
    "full_great_pibling": None,
    "half_pibling": None,
    "full_nibling": "full_first_cousin",
    "half_nibling": None,
    "full_first_cousin": None,
    "child": "sibling-sort",
    "grandchild": "nibling-sort",
    "great_grandchild": "great-nibling-sort",
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
    great_niblings = []
    for relative in relatives:
        new_relation = lookup[relative[1]] 
        if new_relation == "sibling-sort":
            siblings.append(relative[0])
        elif new_relation == "nibling-sort":
            niblings.append(relative[0])
        elif new_relation == "great-nibling-sort":
            great_niblings.append(relative[0])
        else:
            if new_relation is not None:
                relative_updates.append({"base_id": elfling["id"], "relation_id": relative[0], "relationship": new_relation})
                relative_updates.append({"base_id": relative[0], "relation_id": elfling["id"], "relationship": reverse_lookup[relative[1]]})
    
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
            relative_updates.append({"base_id": nibling, "relation_id": elfling["id"], "relationship": "full_pibling"})
        else:
            relative_updates.append({"base_id": elfling["id"], "relation_id": nibling, "relationship": "half_nibling"})
            relative_updates.append({"base_id": nibling, "relation_id": elfling["id"], "relationship": "half_pibling"})

    for great_nibling in great_niblings:
        cursor.execute("SELECT relation_id FROM Relationships WHERE base_id= :base_id AND relationship= :relationship", {"base_id": great_nibling, "relationship": "great_grandparent"})
        great_grandparents = cursor.fetchall()
        if elfling["mother_id"] in great_grandparents and elfling["father_id"] in great_grandparents:
            relative_updates.append({"base_id": elfling["id"], "relation_id": nibling, "relationship": "great_nibling"})
            relative_updates.append({"base_id": nibling, "relation_id": elfling["id"], "relationship": "great_pibling"})

    return relative_updates