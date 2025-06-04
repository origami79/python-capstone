import json
import storage
from elf import Elf
from year import Year

def save_new (file_name: str):
    population = json.dumps(storage.population, default=lambda x: x.__dict__)
    history = json.dumps(storage.history, default=lambda x: x.__dict__)
    filename = file_name + ".json"
    f = open(filename, "w")
    f.write(f"[{population}, {history}]")
    f.close()

def open_file (file_name: str):
    f = open(file_name)
    data = json.load(f)
    print("Data")
    population = data[0]
    history = data[1]
    for index in population:
        entry = population[index]
        id = int(entry['id'])
        elf: Elf = Elf(entry["birth_year"], entry["mother_id"], entry["father_id"], entry["generation"])
        elf.id = id
        elf.spouse_id = entry["spouse_id"]
        elf.death_year = entry["death_year"]
        elf.children = entry["children"]
        elf.first_child_year = entry["first_child_year"]
        elf.last_child_concieved = entry["last_child_concieved"]
        elf.target_children = entry["target_children"]
        elf.gender = entry["gender"]
        storage.population[id] = elf
    print("Finished Elves")
    for index in history:
        entry = history[index]
        id = int(entry["id"])
        year = Year()
        year.alive_at_start = entry["alive_at_start"]
        year.born_this_year = entry["born_this_year"]
        year.died_this_year = entry["died_this_year"]
        storage.history[id] = year
    print("Finished Years")

    f.close()