### structure of a "year" object:
# year num
# alive at start [num]
# born this year [num]
# die this year [num]
from __future__ import annotations
from typing import TYPE_CHECKING
if TYPE_CHECKING:
    from elf import Elf

import itertools
import random
import storage
import elf

class Year:
    id_iter = itertools.count(1)

    def __init__ (self):
        self.id: int = next(Year.id_iter)
        if self.id == 1:
            self.alive_at_start: list[int] = []
        else:
            prev_year: int = self.id - 1
            prev_alive: list[int] = storage.history[prev_year].alive_at_start
            prev_died: list[int] = storage.history[prev_year].died_this_year
            prev_born: list[int] = storage.history[prev_year].born_this_year
            minus_deaths: list[int] = list(set(prev_alive) - set(prev_died))
            plus_births: list[int] = minus_deaths + prev_born
            self.alive_at_start: list[int] = plus_births

        self.born_this_year: list[int] = []
        self.died_this_year: list[int] = []

    def new_birth(self, elf: int):
        self.born_this_year.append(elf)

    def new_death(self, elf: int):
        self.died_this_year.append(elf)

    def alive_at_end (self):
        return list(set(self.alive_at_start) - set(self.died_this_year)) + self.born_this_year

def new_year (auto: bool = True):
    last_year = len(storage.history.keys())
    this_year = last_year + 1
    storage.history[this_year] = Year()
    if auto:
        # attempt to matchmake adult, unmarried elves
        matchmake(this_year)
        # attempt to concieve children
        procreate(this_year)
        # birth any children read to pop
        birth_babies(this_year)
        # kill random small percentage of population
        kill_random(this_year)
    print(f"Finished Year {this_year}")

def all_adults (year_id: int):
    year = storage.history[year_id]
    alive: list[int] = year.alive_at_start
    adults: list[int] = []
    current_year: int = year_id
    for elf_id in alive:
        current_elf: Elf = storage.population[elf_id]
        current_age: int = current_year - current_elf.birth_year
        if current_age >= 50:
            adults.append(elf_id)
    return adults

def adult_unmarried (year_id: int):
    adults: list[int] = all_adults(year_id)
    unmarried: list[int] = []
    for elf_id in adults:
        current_elf: Elf = storage.population[elf_id]
        if not current_elf.married():
            unmarried.append(elf_id)
    return unmarried

def ready_for_a_child (year_id: int):
    adults: list[int] = all_adults(year_id)
    filtered: list[list[int]] = []
    for id in adults:
        current_elf: Elf = storage.population[id]
        if current_elf.spouse_id:
            spouse: Elf = storage.population[current_elf.spouse_id]
            # check if past year of first child
            if current_elf.first_child_year >= year_id:
                # check if not pregnant
                if not current_elf.last_child_concieved or current_elf.last_child_concieved + 10 <= year_id:
                    # check if still looking to have children
                    if spouse and (current_elf.target_children > len(current_elf.children) or spouse.target_children > len(current_elf.children)):
                        filtered.append([id, spouse.id])
    return filtered


def matchmake (year_id: int, marry_chance: int = 50, prefer_match_chance: int = 20, nonprefer_match_chance: int = 10):
    unmarried: list[int] = adult_unmarried(year_id)
    females: list[int] = []
    for id in unmarried:
        current_elf: Elf = storage.population[id]
        if current_elf.gender == "F":
            females.append(id)
    # for each in one list
    for female_id in females:
        # check agianst marry chance
        random_roll = random.randint(1, 100)
        if random_roll <= marry_chance:
            find_husband(female_id, year_id, prefer_match_chance, nonprefer_match_chance)
        # return with no marriage
    
    
def find_husband(female_id: int, year_id, prefer_match_chance, nonprefer_match_chance):
    woman: Elf = storage.population[female_id]
    unmarried: list[int] = adult_unmarried(year_id)
    males: list[int] = []
    for id in unmarried:
        current_elf: Elf = storage.population[id]
        if current_elf.gender == "M":
            males.append(id)
    # remove relatives from list
    near_relatives: list[int] = woman.find_near_relatives()
    valid_partners: list[int] = list(set(males) - set(near_relatives))
    # sort list into preferred (first child year within 10 years) and nonpreferred (all others)
    preferred: list[int] = []
    nonpreferred: list[int] = []
    for male_id in valid_partners:
        man: Elf = storage.population[male_id]
        if abs(woman.first_child_year - man.first_child_year) <= 10:
            preferred.append(male_id)
        else:
            nonpreferred.append(male_id)
    # for each in preferred list
    spouse_found: bool = False
    for male_id in preferred:
        man: Elf = storage.population[male_id]
        # check against another chance (20% maybe?) to find success
        if random.randint(1, 100) <= prefer_match_chance:
            # if succeed, create marriage and continue
            create_marriage(male_id, female_id)
            spouse_found = True
            break
            # if fail skip to next candidate
    # if no success found in preferred list, check in nonpreferred list
    if spouse_found:
        return
    else:
        for male_id in nonpreferred:
            man: Elf = storage.population[male_id]
            # check against another chance (10% maybe?) to find success
            if random.randint(1, 100) <= nonprefer_match_chance:
                # if succeed, create marriage and continue
                create_marriage(male_id, female_id)
                return
            # if fail, no marriage this year and return

def create_marriage (male_id: int, female_id: int):
    man: Elf = storage.population[male_id]
    woman: Elf = storage.population[female_id]
    man.spouse_id = female_id
    woman.spouse_id = male_id
    # print(f"Creating marriage between {man.id} and {woman.id}")

def procreate (year_id: int, child_chance: int = 40):
    # find all couples ready for children
    couples: list[list[int]] = ready_for_a_child(year_id)
    # for each couple
    for couple in couples:
        # roll against child chance
        if random.randint(1, 100) <= child_chance:
            parent1: Elf = storage.population[couple[0]]
            parent2: Elf = storage.population[couple[1]]
            # create a pregnancy
            parent1.last_child_concieved = year_id
            parent2.last_child_concieved = year_id
            # print(f"Creating pregnancy between {parent1.id} and {parent2.id}")

def birth_babies (year_id: int):
    # get all pregnant couples 10 years since last conception
    adults: list[int] = all_adults(year_id)
    due_couples: list[list[int]] = []
    for id in adults:
        adult_elf: Elf = storage.population[id]
        if adult_elf.spouse_id and adult_elf.gender == "M" and adult_elf.last_child_concieved and (year_id - adult_elf.last_child_concieved == 10):
            due_couples.append([adult_elf.id, adult_elf.spouse_id])
        elif adult_elf.spouse_id  and adult_elf.last_child_concieved and (year_id - adult_elf.last_child_concieved == 10):
            due_couples.append([adult_elf.spouse_id, adult_elf.id])
    # for each couple
    for couple in due_couples:
        # create a child for them
        father = storage.population[couple[0]]
        mother = storage.population[couple[1]]
        child = elf.Elf(year_id, mother.id, father.id)
        father.children.append(child.id)
        mother.children.append(child.id)
        storage.history[year_id].born_this_year.append(child.id)
        storage.population[child.id] = child
        # print(f"Creating child between {father.id} and {mother.id}")
    
def kill_random (year_id: int, adult_death_chance: int = 2, child_death_chance: int = 1):
    # get all alive
    year = storage.history[year_id]
    alive: list[int] = year.alive_at_start
    adults: list[int] = []
    children: list[int] = []
    current_year: int = year_id
    # sort into adult and child
    for elf_id in alive:
        current_elf: Elf = storage.population[elf_id]
        current_age: int = current_year - current_elf.birth_year
        if current_age >= 50:
            adults.append(elf_id)
        else:
            children.append(elf_id)
    # for each adult check against adult death chance
    for adult_id in adults:
        # if success
        if random.randint(1, 500) <= adult_death_chance:
            adult: Elf = storage.population[adult_id]
            # add to died this year
            year.died_this_year.append(adult_id)
            # update elf with death
            adult.death_year = year_id
            # print(f"Unfortunately, {adult.id} has been killed!")
    # for each child check against child death chance
    for child_id in children:
        # if success
        if random.randint(1, 500) <= child_death_chance:
            child: Elf = storage.population[child_id]
            # add to died this year
            year.died_this_year.append(child_id)
            # update elf with death
            child.death_year = year_id
            # print(f"Unfortunately, {child.id} has been killed!")