import sqlite3
from parameters import file_name


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


conn.close()