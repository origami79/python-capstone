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
from tracemalloc import start
import storage

class Elf:
    id_iter = itertools.count(1)

    def __init__ (self, birth_year, mother_id, father_id, spouse_id = None, target_children = None, gender = None):
        self.id = next(Elf.id_iter)
        self.birth_year = birth_year
        self.mother_id = mother_id
        self.father_id = father_id
        self.spouse_id = spouse_id
        self.death_year = None
        self.children = []
        self.last_child = None
        self.target_children = target_children or random.choice([0, 1, 1, 2, 2, 2, 3, 3, 4, 5, 6])
        if self.target_children == 0:
            self.enough_children = True
        else:
            self.enough_children = False
        self.gender = gender or choose_gender()

    def __str__ (self) -> str:
        return f"Elf {self.id} is {self.gender}"
    
    def find_near_relatives (self):
    # first degree - self, parents, children, siblings
        parents = []
        if self.mother_id:
            parents.append(self.mother_id)
        if self.father_id:
            parents.append(self.father_id)
        children = self.children
        siblings = []
        for parent in parents:
            if parent:
                siblings += storage.population[children].children
        first_degree_relatives = list(set(parents + children + siblings))
        # second degree - grandparents, grandchildren, aunt/uncle, niece/nephew
        grandparents = []
        for parent in parents:
            if parent:
                grandparents += [storage.population[parent].mother_id, storage.population[parent].father_id]
        grandchildren = []
        for child in children:
            if child:
                grandchildren += storage.population[child].children
        piblings = []
        for grandparent in grandparents:
            if grandparent:
                piblings += storage.population[grandparent].children
        niblings = []
        for sibling in siblings:
            if sibling:
                niblings += storage.population[sibling].children
        second_degree_relatives = list(set(grandparents + grandchildren + piblings + niblings))

        return list(set(first_degree_relatives + second_degree_relatives))
    
    def pick_spouse (self, year):
        target_gender = "M" if self.gender == "F" else "F"
        all_alive = storage.history[year].alive_at_start
        near_relatives = self.find_near_relatives()
        unrelated = list(set(all_alive) - set(near_relatives))
        filtered = []
        for id in unrelated:
            elf = storage.population[id]
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

def procreate (elf_id, year):
    gender = storage.population[elf_id].gender
    spouse = storage.population[elf_id].spouse_id
    if gender == "M":
        father_id = elf_id
        mother_id = spouse or storage.population[elf_id].pick_spouse(year)
    else:
        mother_id = elf_id
        father_id = spouse or storage.population[elf_id].pick_spouse(year)

    




