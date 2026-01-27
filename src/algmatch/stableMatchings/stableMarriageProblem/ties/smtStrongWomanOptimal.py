"""
Algorithm to produce M_z, the woman-optimal, man-pessimal strongly stable matching, where such a thing exists.
"""

from algmatch.stableMatchings.stableMarriageProblem.ties.smtStrongAbstract import (
    SMTStrongAbstract,
)


class SMTStrongWomanOptimal(SMTStrongAbstract):
    def __init__(
        self, filename: str | None = None, dictionary: dict | None = None
    ) -> None:
        super().__init__(filename=filename, dictionary=dictionary)

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
        if man in self.women:
            man, woman = woman, man
        self.unassigned_women.add(woman)

    def _get_critical_set(self):
        self._get_maximum_matching()

        unexplored_women = {
            w for w, m in self.maximum_matching["women"].items() if m is None
        }
        explored_women, visited_men = set(), set()
        while unexplored_women:
            woman = unexplored_women.pop()
            explored_women.add(woman)
            men_to_explore = self.M[woman]["assigned"] - {
                self.maximum_matching["women"][woman]
            }

            for m in men_to_explore:
                if m not in visited_men:
                    visited_men.add(m)
                    m_match = self.maximum_matching["men"][m]
                    if m_match not in explored_women:
                        unexplored_women.add(m_match)

        return explored_women

    def _while_loop(self) -> bool:
        U = {None}
        while U:
            while len(self.unassigned_women) != 0:
                w = self.unassigned_women.pop()
                m_tie = self._get_head(w)
                for m in m_tie.copy():
                    self._engage(w, m)
                    self.proposed[m] = True
                    self._reject_lower_ranks(m, w)

            Z = self._get_critical_set()
            U = self._neighbourhood(Z)
            for m in U:
                self._break_all_engagements(m)
                self._delete_tail(m)

        self._select_maximum_matching()

        # check viability of matching
        for m in self.men:
            if self.M[m]["assigned"] is None and self.proposed[m]:
                return False
        return True
