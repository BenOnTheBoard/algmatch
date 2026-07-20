"""
Algorithm to produce M_z, the woman-optimal, man-pessimal super-stable matching, where such a thing exists.
"""

from algmatch.stableMatchings.stableMarriageProblem.ties.smtAbstract import SMTAbstract
from algmatch.abstractClasses.preferenceSource import PreferenceSource
from algmatch.abstractClasses.stabilityType import StabilityType


class SMTSuperWomanOriented(SMTAbstract):
    def __init__(self, source: PreferenceSource) -> None:
        super().__init__(source, StabilityType.SUPER)

        self.unassigned_women = set()
        self.proposed = {m: False for m in self.men}

        for man in self.men:
            self.M[man] = {"assigned": set()}

        for woman, prefs in self.women.items():
            if len(prefs["list"]) > 0:
                self.unassigned_women.add(woman)
            self.M[woman] = {"assigned": set()}

    def _delete_pair(self, man, woman) -> None:
        super()._delete_pair(man, woman)
        if man in self.women:
            man, woman = woman, man
        if self._get_pref_length(woman) == 0:
            self.unassigned_women.discard(woman)

    def _break_engagement(self, man, woman):
        super()._break_engagement(man, woman)
        if woman in self.men:
            man, woman = woman, man
        self.unassigned_women.add(woman)

    def _while_loop(self) -> bool:
        while len(self.unassigned_women) != 0:
            w = self.unassigned_women.pop()
            m_tie = self._get_head(w)
            for m in m_tie.copy():
                self._engage(m, w)
                self.proposed[m] = True
                self._reject_lower_ranks(m, w)

                if len(self.M[m]["assigned"]) > 1:
                    self._break_all_engagements(m)
                    self._delete_tail(m)

        woman_multiply_assigned = False
        for m in self.men:
            if len(self.M[m]["assigned"]) > 1:
                woman_multiply_assigned = True

        for person_info in self.M.values():
            if person_info["assigned"]:
                person_info["assigned"] = next(iter(person_info["assigned"]))
            else:
                person_info["assigned"] = None

        # check viability of matching
        if woman_multiply_assigned:
            return False
        for m in self.men:
            if self.M[m]["assigned"] is None and self.proposed[m]:
                return False
        return True
