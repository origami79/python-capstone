import sqlite3

conn = sqlite3.connect("tolkien_elves.db")
cursor = conn.cursor()


cursor.execute('SELECT id FROM Elves WHERE death_year IS NULL')
living_elves = cursor.fetchall()

cursor.execute('SELECT id FROM Elves WHERE death_year IS NULL AND birth_year >= 550')
child_elves = cursor.fetchall()

cursor.execute('SELECT id FROM Elves WHERE death_year IS NOT NULL')
dead_elves = cursor.fetchall()

cursor.execute('Select generation, COUNT(id) FROM Elves GROUP BY generation')
generations = cursor.fetchall()

# for elf in elves:
#     print(elf)
print(f"Living: {len(living_elves)}")
print(f"Adults: {len(living_elves) - len(child_elves)}, Children: {len(child_elves)}")
print(f"Generations: {generations}")
print(f"Dead: {len(dead_elves)}")

conn.close()