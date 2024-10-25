"""
Algorithm to produce M_0, the man-optimal, woman-pessimal stable matching, where such a thing exists.
"""

from copy import deepcopy

from stableMatchings.stableMarriageProblem.smAbstract import SMAbstract

class SMManOptimal(SMAbstract):
    def __init__(self, filename: str | None = None, dictionary: dict | None = None) -> None:
        super().__init__(filename=filename, dictionary=dictionary)

        self.unassigned_men = set()

        for man in self.men:
            self.unassigned_men.add(man)
            self.M[man] = {"assigned": None}

        for woman in self.women:
            self.M[woman] = {"assigned": None}

    def _delete_pair(self, man, woman):         
        self.men[man]['list'].remove(woman)
        self.women[woman]['list'].remove(man)

    def _engage(self, man, woman):
        self.M[man]["assigned"] = woman
        self.M[woman]["assigned"] = man

    def _free_up(self, man):
        self.M[man]["assigned"] = None
        self.unassigned_men.add(man)
 
    def _while_loop(self):
        while len(self.unassigned_men) != 0:
            m = self.unassigned_men.pop()
            w = self.men[m]["list"][0]
            p = self.M[w]["assigned"]

            if p is not None:
                self._free_up(p)
            self._engage(m,w)

            rank_m = self.women[w]["rank"][m]
            for reject in self.women[w]["list"][rank_m+1:]:
                self._delete_pair(reject,w)