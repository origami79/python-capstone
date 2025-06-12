import sqlite3
from parameters import file_name, adulthood, pregnancy, time_between_children


conn = sqlite3.connect(f"{file_name}.db")
cursor = conn.cursor()

# # cursor.execute('SELECT id, birth_year FROM Elves')
# # elves = cursor.fetchall()
# # for elf in elves:
# #     print(f"Elf {elf[0]} born in {elf[1]}")

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

original_search = 0
new_search = 0
for i in range (1, 600):
    year = i

    # cursor.execute('''
    #     SELECT * FROM Elves WHERE gender= "M" AND birth_year <= :year_for_adult AND death_year IS NULL
    # ''', {"year_for_adult": year - adulthood})
    # new_search += len(cursor.fetchall())  

    # cursor.execute('''
    #     SELECT * FROM Elves WHERE gender= "F" AND birth_year <= :year_for_adult AND death_year IS NULL AND (last_child_conceived IS NULL OR last_child_conceived >= :year_of_birth)
    # ''', {"year_for_adult": year - adulthood, "year": 600, "year_of_birth": 600 - (pregnancy)})
    # new_search += len(cursor.fetchall())  

    # cursor.execute('''
    #     SELECT * FROM Elves WHERE (gender= "M" AND birth_year <= :year_for_adult AND death_year IS NULL) OR 
    #         (gender= "F" AND birth_year <= :year_for_adult AND death_year IS NULL AND ((first_child_year >= :year AND last_child_conceived IS NULL) OR (last_child_conceived >= :last_conception)))
    # ''', {"year_for_adult": year - adulthood, "year": year, "last_conception": year - (pregnancy + time_between_children)})
    # original_search += len(cursor.fetchall())  

    # cursor.execute('''
    #     SELECT * FROM Elves WHERE gender= "M" AND birth_year <= :year_for_adult AND death_year IS NULL
    # ''', {"year_for_adult": year - adulthood})
    # original_search += len(cursor.fetchall())   

    cursor.execute('''
        SELECT * FROM Elves WHERE gender= "F" AND birth_year <= :year_for_adult AND (death_year IS NULL OR death_year >= :year) AND (last_child_conceived IS NULL OR last_child_conceived >= :long_enough_since_conception)
    ''', {"year_for_adult": year - adulthood, "year": year, "long_enough_since_conception": year - (pregnancy)})
    original_search += len(cursor.fetchall())     

print(f"Potential Joint Adult Victims: {original_search}, Separated Adults: {new_search}")


conn.close()