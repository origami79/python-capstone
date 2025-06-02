import elf
import year
import storage

year_one = year.Year()

# for i in range(144):
for i in range(14):
    if i % 2 == 0:
        new_elf = elf.Elf(-50, None, None, None, 6, "M")
    else:
        new_elf = elf.Elf(-50, None, None, None, 6, "F")
    storage.population[i + 1] = new_elf
    year_one.new_birth(i + 1)
    storage.history[1] = year_one
    # print(new_elf)

# for index in storage.population:
#     print(storage.population[index])
storage.history[2] = year.Year()

print('spouse', elf.procreate(1,2))
