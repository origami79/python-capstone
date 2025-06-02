import elf
import year
import storage

year_one = year.Year(auto = False)

# for i in range(144):
for i in range(14):
    if i % 2 == 0:
        new_elf = elf.Elf(-50, None, None, None, 6, "M")
    else:
        new_elf = elf.Elf(-50, None, None, None, 6, "F")
    storage.population[i + 1] = new_elf
    year_one.new_birth(i + 1)
    # print(new_elf)
storage.history[1] = year_one
storage.history[2] = year.Year()

for index in storage.population:
    print("Population:", storage.population[index])
for index in storage.history:
    print("Year:", index, ", Population:", len(storage.history[index].alive_at_end()))

# print('spouse', elf.procreate(1,2))
