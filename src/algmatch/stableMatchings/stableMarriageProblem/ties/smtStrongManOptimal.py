"""
Algorithm to produce M_0, the man-optimal, woman-pessimal strongly stable matching, where such a thing exists.
"""

from algmatch.stableMatchings.stableMarriageProblem.ties.smtStrongAbstract import (
    SMTStrongAbstract,
)


class SMTStrongManOptimal(SMTStrongAbstract):
    def __init__(
        self, filename: str | None = None, dictionary: dict | None = None
    ) -> None:
        super().__init__(filename=filename, dictionary=dictionary)

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

    def _get_critical_set(self):
        self._get_maximum_matching()

        unexplored_men = {
            m for m, w in self.maximum_matching["men"].items() if w is None
        }
        explored_men, visited_women = set(), set()
        while unexplored_men:
            man = unexplored_men.pop()
            explored_men.add(man)
            women_to_explore = self.M[man]["assigned"] - {
                self.maximum_matching["men"][man]
            }

            for w in women_to_explore:
                if w not in visited_women:
                    visited_women.add(w)
                    w_match = self.maximum_matching["women"][w]
                    if w_match not in explored_men:
                        unexplored_men.add(w_match)

        return explored_men

    def _while_loop(self) -> bool:
        U = {None}
        while U:
            while len(self.unassigned_men) != 0:
                m = self.unassigned_men.pop()
                w_tie = self._get_head(m)
                for w in w_tie.copy():
                    self._engage(m, w)
                    self.proposed[w] = True
                    self._reject_lower_ranks(w, m)

            Z = self._get_critical_set()
            U = self._neighbourhood(Z)
            for w in U:
                self._break_all_engagements(w)
                self._delete_tail(w)

        self._select_maximum_matching()

        # check viability of matching
        for w in self.women:
            if self.M[w]["assigned"] is None and self.proposed[w]:
                return False
        return True
