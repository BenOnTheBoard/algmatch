"""
Algorithm to produce M_z, the woman-optimal, man-pessimal stable matching, where such a thing exists.
"""

from algmatch.stableMatchings.stableMarriageProblem.noTies.smAbstract import SMAbstract
from algmatch.abstractClasses.preferenceSource import PreferenceSource


class SMWomanOptimal(SMAbstract):
    def __init__(self, source: PreferenceSource) -> None:
        super().__init__(source)
        self.unassigned_women = set()

        for man in self.men:
            self.M[man] = {"assigned": None}

        for woman, prefs in self.women.items():
            if len(prefs["list"]) > 0:
                self.unassigned_women.add(woman)
            self.M[woman] = {"assigned": None}

    def _delete_pair(self, man, woman):
        self.men[man]["list"].remove(woman)
        self.women[woman]["list"].remove(man)
        if len(self.women[woman]["list"]) == 0:
            self.unassigned_women.discard(woman)

    def _engage(self, man, woman):
        self.M[man]["assigned"] = woman
        self.M[woman]["assigned"] = man

    def _free_up(self, woman):
        self.M[woman]["assigned"] = None
        if len(self.women[woman]["list"]) > 0:
            self.unassigned_women.add(woman)

    def _while_loop(self):
        while len(self.unassigned_women) != 0:
            w = self.unassigned_women.pop()
            m = self.women[w]["list"][0]
            p = self.M[m]["assigned"]

            if p is not None:
                self._free_up(p)
            self._engage(m, w)

            rank_w = self.men[m]["rank"][w]
            for reject in self.men[m]["list"][rank_w + 1 :]:
                self._delete_pair(m, reject)
