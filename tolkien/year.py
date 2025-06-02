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
import storage

class Year:
    id_iter = itertools.count(1)

    def __init__ (self, auto: bool = True):
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

        if auto:
            # attempt to matchmake adult, unmarried elves
            # attempt to concieve children
            # birth any children read to pop
            # kill random percentage of population
            pass

    def new_birth(self, elf: int):
        self.born_this_year.append(elf)

    def new_death(self, elf: int):
        self.died_this_year.append(elf)

    def alive_at_end (self):
        return list(set(self.alive_at_start) - set(self.died_this_year)) + self.born_this_year

def all_adults (year_id: int):
    year = storage.history[year_id]
    alive: list[int] = year.alive_at_start
    adults: list[int] = []
    current_year: int = year_id
    for elf_id in alive:
        elf: Elf = storage.population[elf_id]
        current_age: int = current_year - elf.birth_year
        if current_age >= 50:
            adults.append(elf_id)
    return adults

def adult_unmarried (year_id: int):
    adults: list[int] = all_adults(year_id)
    unmarried: list[int] = []
    for elf_id in adults:
        elf: Elf = storage.population[elf_id]
        if not elf.married:
            adults.append(elf_id)
    return unmarried

def ready_for_a_child (year_id: int):
    adults: list[int] = all_adults(year_id)
    filtered: list[list[int]] = []
    for id in adults:
        elf: Elf = storage.population[id]
        if elf.spouse_id:
            spouse: Elf = storage.population[elf.spouse_id]
        # check if past year of first child
        if elf.first_child_year >= year_id:
            # check if not pregnant
            if not elf.last_child_concieved or elf.last_child_concieved + 10 <= year_id:
                # check if still looking to have children
                if spouse and (elf.target_children > len(elf.children) or spouse.target_children > len(elf.children)):
                    filtered.append([id, spouse.id])
    return filtered

def matchmake (year_id: int, marry_chance: int = 50):
    unmarried: list[int] = adult_unmarried(year_id)
    male: list[int] = []
    female: list[int] = []
    for id in unmarried:
        elf: Elf = storage.population[id]
        if elf.gender == "M":
            male.append(id)
        else:
            female.append(id)
    # for each in one list
        # check agianst marry chance
            # remove relatives from list
            # sort list into preferred (first child year within 10 years) and nonpreferred (all others)
            # for each in preferred list
                # check against another chance (20% maybe?) to find success
                    # if succeed, create marriage and return
                    # if fail skip to next candidate
            # if no success found in preferred list, check in nonpreferred list
                # check against another chance (10% maybe?) to find success
                    # if success, create marriage and return
                    # if fail, no marriage this year and return
        # return with no marriage
