import sqlite3

conn = sqlite3.connect("examine_this.db")
cursor = conn.cursor()

# cursor.execute('SELECT id, birth_year FROM Elves')
# elves = cursor.fetchall()
# for elf in elves:
#     print(f"Elf {elf[0]} born in {elf[1]}")

# cursor.execute('SELECT id FROM Elves WHERE death_year IS NULL')
# living_elves = cursor.fetchall()

# cursor.execute('SELECT id FROM Elves WHERE death_year IS NULL AND birth_year >= 550')
# child_elves = cursor.fetchall()

# cursor.execute('SELECT id FROM Elves WHERE death_year IS NOT NULL')
# dead_elves = cursor.fetchall()

# cursor.execute('Select generation, COUNT(id) FROM Elves GROUP BY generation')
# generations = cursor.fetchall()

# print(f"Living: {len(living_elves)}")
# print(f"Adults: {len(living_elves) - len(child_elves)}, Children: {len(child_elves)}")
# print(f"Generations: {generations}")
# print(f"Dead: {len(dead_elves)}")

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
    "full_great_nibling": None,
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

def repair_relationships (elfling):
    cursor.execute("Select Relationships.relation_id, Relationships.relationship FROM Relationships INNER JOIN Elves ON Relationships.relation_id = Elves.id AND base_id IN (?, ?)", [elfling[1], elfling[2]])
    relatives = cursor.fetchall()

    relative_updates = []
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
                relative_updates.append({"base_id": elfling[0], "relation_id": relative[0], "relationship": new_relation})
                relative_updates.append({"base_id": relative[0], "relation_id": elfling[0], "relationship": reverse_lookup[relative[1]]})
    
    while len(siblings) > 0:
        current = siblings.pop()
        if current in siblings:
            relative_updates.append({"base_id": elfling[0], "relation_id": current, "relationship": "full_sibling"})
            relative_updates.append({"base_id": current, "relation_id": elfling[0], "relationship": "full_sibling"})
            siblings.remove(current)
        else:
            relative_updates.append({"base_id": elfling[0], "relation_id": current, "relationship": "half_sibling"})
            relative_updates.append({"base_id": current, "relation_id": elfling[0], "relationship": "half_sibling"})

    for nibling in set(niblings):
        cursor.execute("SELECT relation_id FROM Relationships WHERE base_id= :base_id AND relationship= :relationship", {"base_id": nibling, "relationship": "grandparent"})
        grandparents = list(map(lambda data: data[0], cursor.fetchall()))
        print(f"Nibling ID: {nibling}, Grandparents: {grandparents}")
        if elfling["mother_id"] in grandparents and elfling["father_id"] in grandparents:
            relative_updates.append({"base_id": elfling[0], "relation_id": nibling, "relationship": "full_nibling"})
            relative_updates.append({"base_id": nibling, "relation_id": elfling[0], "relationship": "full_pibling"})
        else:
            relative_updates.append({"base_id": elfling[0], "relation_id": nibling, "relationship": "half_nibling"})
            relative_updates.append({"base_id": nibling, "relation_id": elfling[0], "relationship": "half_pibling"})

    for great_nibling in set(great_niblings):
        cursor.execute("SELECT relation_id FROM Relationships WHERE base_id= :base_id AND relationship= :relationship", {"base_id": great_nibling, "relationship": "great_grandparent"})
        great_grandparents = list(map(lambda data: data[0], cursor.fetchall()))
        if elfling["mother_id"] in great_grandparents and elfling["father_id"] in great_grandparents:
            relative_updates.append({"base_id": elfling[0], "relation_id": nibling, "relationship": "great_nibling"})
            relative_updates.append({"base_id": nibling, "relation_id": elfling[0], "relationship": "great_pibling"})

    cursor.executemany("INSERT INTO Relationships (base_id, relation_id, relationship) VALUES (:base_id, :relation_id, :relationship)", relative_updates)
    conn.commit()

def fix_relationships():
    # cursor.execute("DELETE FROM Relationships WHERE relationship IS NOT 'parent' OR relationship IS NOT 'child'")
    # conn.commit()
    cursor.execute("SELECT id, mother_id, father_id FROM Elves WHERE generation IS NOT 1")
    elves = cursor.fetchall()
    for elf in elves:
        repair_relationships(elf)


fix_relationships()


conn.close()