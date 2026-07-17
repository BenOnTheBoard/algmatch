"""
Algorithm to produce M_0, the man-optimal, woman-pessimal super-stable matching, where such a thing exists.
"""

from algmatch.stableMatchings.stableMarriageProblem.ties.smtAbstract import SMTAbstract
from algmatch.abstractClasses.stabilityType import StabilityType


class SMTSuperManOriented(SMTAbstract):
    def __init__(
        self, filename: str | None = None, dictionary: dict | None = None
    ) -> None:
        super().__init__(
            filename=filename, dictionary=dictionary, stability_type=StabilityType.SUPER
        )

        self.unassigned_men = set()
        self.proposed = {w: False for w in self.women}

        for man, prefs in self.men.items():
            if len(prefs["list"]) > 0:
                self.unassigned_men.add(man)
            self.M[man] = {"assigned": set()}

        for woman in self.women:
            self.M[woman] = {"assigned": set()}

    def _delete_pair(self, man, woman) -> None:
        super()._delete_pair(man, woman)
        if man in self.women:
            man, woman = woman, man
        if self._get_pref_length(man) == 0:
            self.unassigned_men.discard(man)

    def _break_engagement(self, man, woman):
        super()._break_engagement(man, woman)
        if man in self.women:
            man, woman = woman, man
        self.unassigned_men.add(man)

    def _while_loop(self) -> bool:
        while len(self.unassigned_men) != 0:
            m = self.unassigned_men.pop()
            w_tie = self._get_head(m)
            for w in w_tie.copy():
                self._engage(m, w)
                self.proposed[w] = True
                self._reject_lower_ranks(w, m)

                if len(self.M[w]["assigned"]) > 1:
                    self._break_all_engagements(w)
                    self._delete_tail(w)

        man_multiply_assigned = False
        for m in self.men:
            if len(self.M[m]["assigned"]) > 1:
                man_multiply_assigned = True

        for person_info in self.M.values():
            if person_info["assigned"]:
                person_info["assigned"] = next(iter(person_info["assigned"]))
            else:
                person_info["assigned"] = None

        # check viability of matching
        if man_multiply_assigned:
            return False
        for w in self.women:
            if self.M[w]["assigned"] is None and self.proposed[w]:
                return False
        return True
