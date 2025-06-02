### structure of a "year" object:
# year num
# alive at start [num]
# born this year [num]
# die this year [num]

import itertools
import storage

class Year:
    id_iter = itertools.count(1)

    def __init__ (self):
        self.id = next(Year.id_iter)
        if self.id == 1:
            self.alive_at_start = []
        else:
            prev_year = self.id - 1
            prev_alive = storage.history[prev_year].alive_at_start
            prev_died = storage.history[prev_year].died_this_year
            prev_born = storage.history[prev_year].born_this_year
            minus_deaths = list(set(prev_alive) - set(prev_died))
            plus_births = minus_deaths + prev_born
            self.alive_at_start = plus_births

        self.born_this_year = []
        self.died_this_year = []

    def new_birth(self, elf):
        self.born_this_year.append(elf)

    def new_death(self, elf):
        self.died_this_year.append(elf)

    def alive_at_end (self):
        return list(set(self.alive_at_start) - set(self.died_this_year)) + self.born_this_year
