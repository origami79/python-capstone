import random
from typing import Union
from collections import namedtuple

Elf = namedtuple( "Elf", [
    "id",
    "mother_id",
    "father_id",
    "birth_year",
    "death_year",
    "generation",
    "gender",
    "spouse_id",
    "target_children",
    "first_child_year",
    "last_child_conceived",
    "father_of_baby"
    ]
)

def new_elf(birth_year: int, generation: int, mother_id: Union[int, None] = None, father_id: Union[int, None] = None, spouse_id: Union[int, None] = None, gender: Union[str, None] = None):
    elf = {
        "mother_id": mother_id,
        "father_id": father_id,
        "birth_year": birth_year,
        "death_year": None,
        "generation": generation,
        "gender": gender or random_gender(),
        "spouse_id": spouse_id,
        "target_children": None,
        "first_child_year": None,
        "last_child_conceived": None,
        "father_of_baby": None
    } 
    elf["target_children"] = calculate_target_children(elf["generation"])
    elf["first_child_year"] = calculate_first_child_year(elf["generation"], elf["target_children"], elf["birth_year"],)
    return elf

def format_elf(elf_data: tuple):
    elf = Elf(*elf_data)
    return elf

def random_gender():
    return random.choice(["F", "M"])

def calculate_target_children(generation):
    average_six = [4, 4, 5, 5, 5, 6, 6, 6, 6, 6, 6, 6, 6, 6, 6, 6, 6, 6, 6, 6, 6, 6, 6, 6, 6, 6, 6, 6, 6, 6]
    average_five = [2, 2, 2, 3, 3, 3, 4, 4, 4, 4, 4, 4, 5, 5, 5, 5, 5, 5, 5, 5, 5, 5, 5, 5, 5, 5, 6, 6, 6, 6]
    average_four = [0, 1, 1, 2, 2, 2, 3, 3, 3, 3, 4, 4, 4, 4, 4, 4, 4, 4, 4, 4, 4, 4, 4, 4, 5, 5, 5, 5, 6, 6]
    average_three = [0, 0, 1, 1, 1, 1, 1, 2, 2, 2, 2, 2, 2, 3, 3, 3, 3, 3, 3, 3, 3, 4, 4, 4, 4, 5, 5, 5, 6, 6]
    if generation in [1, 2, 3]:
        return random.choice(average_six)
    elif generation in [4, 5, 6]:
        return random.choice(average_five)
    elif random.randint(1, 100) % 2 == 0:
        return random.choice(average_four)
    else:
        return random.choice(average_three)

def calculate_first_child_year(generation, target_children, birth_year):
    if target_children == 0:
        return None
    else:
        if generation in [1, 2, 3]:
            return random.randint(50, 60) + birth_year
        elif generation in [4, 5, 6]:
            return random.randint(50, 75) + birth_year
        elif random.randint(1, 100) % 2 == 0:
            return random.randint(50, 150) + birth_year
        else:
            return random.randint(75, 200) + birth_year
