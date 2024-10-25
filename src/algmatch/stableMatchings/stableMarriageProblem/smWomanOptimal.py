"""
Algorithm to produce M_z, the woman-optimal, man-pessimal stable matching, where such a thing exists.
"""

import os
from stableMatchings.stableMarriageProblem.smAbstract import SMAbstract


class SMWomanOptimal(SMAbstract):
    def __init__(self, filename: str | None = None, dictionary: dict | None = None) -> None:
        super().__init__(filename=filename, dictionary=dictionary)

        self.unassigned_women = set()

        for man in self.men:
            self.M[man] = {"assigned": None}

        for woman in self.women:
            self.unassigned_women.add(woman)
            self.M[woman] = {"assigned": None}

    def _delete_pair(self, man, woman):         
        self.men[man]['list'].remove(woman)
        self.women[woman]['list'].remove(man)

    def _engage(self, man, woman):
        self.M[man]["assigned"] = woman
        self.M[woman]["assigned"] = man

    def _free_up(self, woman):
        self.M[woman]["assigned"] = None
        self.unassigned_women.add(woman)
 
    def _while_loop(self):
        while len(self.unassigned_women) != 0:
            w = self.unassigned_women.pop()
            m = self.women[w]["list"][0]
            p = self.M[m]["assigned"]

            if p is not None:
                self._free_up(p)
            self._engage(m,w)

            rank_w = self.men[m]["rank"][w]
            for reject in self.men[m]["list"][rank_w+1:]:
                self._delete_pair(m,reject)