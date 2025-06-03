### structure of an "elf" object:
# id num
# sex string
# birth year num
# death year num
# mother id num
# father id num
# children ids [num]
# enough children bool

import itertools
import random
from typing import Union
import storage
import year

class Elf:
    id_iter = itertools.count(1)

    def __init__ (self, birth_year: int, mother_id: Union [int, None], father_id: Union [int, None], spouse_id: Union [int, None] = None, target_children: Union [int, None] = None, gender: Union [str, None] = None, first_child_age: Union [int, None] = None, id: Union [str, int, None] = None):
        if not id:
            self.id: int = next(Elf.id_iter)
        else:
            self.id: int = int(id)
        self.birth_year: int = birth_year
        self.mother_id: Union [int, None] = mother_id
        self.father_id: Union [int, None] = father_id
        self.spouse_id: Union [int, None] = spouse_id
        self.death_year: Union [int, None] = None
        self.children: list[int] = []
        self.first_child_year: int = self.first_child(first_child_age)
        # applies to BOTH parents; 
        self.last_child_concieved: Union [int, None] = None
        # applies to BOTH parents; used to calculate both the due date and the point when another child can be concieved
        self.target_children: int = target_children or random.choice([0, 1, 1, 2, 2, 2, 3, 3, 4, 5, 6])

        self.gender: str = gender or choose_gender()

    def __str__ (self) -> str:
        return f"Elf {self.id} is {self.gender}, is married to Elf {self.spouse_id} and wants {self.target_children} children, starting in {self.first_child_year}"
    
    def first_child (self, first_child_age: Union [int, None]):
        if first_child_age:
            return first_child_age + self.birth_year
        else:
            return random.randint(50, 200) + self.birth_year


    def enough_children (self):
        if len(self.children) >= self.target_children:
            return True
        else:
            return False
    
    def find_near_relatives (self):
    # first degree - self, parents, children, siblings
        parents: list[int] = []
        if self.mother_id:
            parents.append(self.mother_id)
        if self.father_id:
            parents.append(self.father_id)
        children = self.children
        siblings: list[int] = []
        for parent in parents:
            if parent:
                siblings += storage.population[parent].children
        first_degree_relatives: list[int] = list(set(parents + children + siblings))
        # second degree - grandparents, grandchildren, aunt/uncle, niece/nephew
        grandparents: list[int] = []
        for parent in parents:
            if parent:
                grandmother = storage.population[parent].mother_id
                grandfather = storage.population[parent].father_id
                if grandmother:
                    grandparents.append(grandmother)
                if grandfather:
                    grandparents.append(grandfather)
        grandchildren: list[int] = []
        for child in children:
            if child:
                grandchildren += storage.population[child].children
        piblings: list[int] = []
        for grandparent in grandparents:
            if grandparent:
                piblings += storage.population[grandparent].children
        niblings: list[int] = []
        for sibling in siblings:
            if sibling:
                niblings += storage.population[sibling].children
        second_degree_relatives: list[int] = list(set(grandparents + grandchildren + piblings + niblings))

        return list(set(first_degree_relatives + second_degree_relatives))
    
    def pick_spouse (self, year_id: int):
        target_gender: str = "M" if self.gender == "F" else "F"
        unmarried: list[int] = year.adult_unmarried(year_id)
        near_relatives: list[int] = self.find_near_relatives()
        unrelated: list[int] = list(set(unmarried) - set(near_relatives))
        filtered: list[int] = []
        for id in unrelated:
            elf: Elf = storage.population[id]
            if elf.gender == target_gender and not elf.enough_children:
                filtered.append(id)

        print('filtered', filtered)

    def married (self):
        if self.spouse_id:
            return True
        else:
            return False

def choose_gender ():
    return random.choice(["F", "M"])

def pregnant (elf_id: int, year_id: int):
    elf: Elf = storage.population[elf_id]
    last_child = elf.last_child_concieved
    if last_child and last_child + 10 < year_id:
        return True
    else:
        return False


    




