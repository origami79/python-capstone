import elf
import year
import storage

year_one = year.Year()

for i in range(144):
# for i in range(14):
    if i % 2 == 0:
        new_elf = elf.Elf(-50, None, None, None, 6, "M")
    else:
        new_elf = elf.Elf(-50, None, None, None, 6, "F")
    storage.population[i + 1] = new_elf
    year_one.new_birth(i + 1)
    # print(new_elf)
storage.history[1] = year_one

# test out new year
for i in range(1000):
    year.new_year()

currently_alive = []
currently_dead = []
currently_adult = []
currently_child = []
current_year = len(storage.history.keys())

for i in storage.population:
    this_elf = storage.population[i]
    if this_elf.death_year:
        currently_dead.append(this_elf.id)
    else:
        currently_alive.append(this_elf.id)
        current_age = current_year - this_elf.birth_year
        if current_age < 50:
            currently_child.append(this_elf.id)
        else:
            currently_adult.append(this_elf.id)

print(f"There are currently {len(currently_alive)} elves alive, {len(currently_child)} of whom are children, and {len(currently_dead)} elves who have died.")
# print(f"Currently dead elves are: {currently_dead}")
