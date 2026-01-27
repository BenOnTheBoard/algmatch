"""
Hospital/Residents Problem With Ties - Strong-Stability-Specific Abstract Class
Stores implementations of:
- Gabow's algorithm for maximum matching
- Finding the critical set of residents based on the above
- Definition of domination
"""

from collections import deque
from copy import deepcopy

from algmatch.stableMatchings.hospitalResidentsProblem.ties.hrtAbstract import (
    HRTAbstract,
)


class HRTStrongAbstract(HRTAbstract):
    def __init__(
        self, filename: str | None = None, dictionary: dict | None = None
    ) -> None:
        super().__init__(
            filename=filename, dictionary=dictionary, stability_type="strong"
        )
        # used to find the critical set and final answer
        self.maximum_matching = {}
        self.dist = {}
        self.G_r = {}

    def _reset_G_r(self):
        self.G_r = deepcopy(self.M)
        for hospital, h_info in self.hospitals.items():
            self.G_r[hospital]["quota"] = h_info["capacity"]

    def _reset_maximum_matching(self):
        self.maximum_matching = {
            "residents": {r: None for r in self.residents if r in self.G_r},
            "hospitals": {h: set() for h in self.hospitals},
        }
        self.dist = {}

    def _remove_from_G_r(self, resident):
        for hospital in self.G_r[resident]["assigned"]:
            self.G_r[hospital]["assigned"].remove(resident)
        del self.G_r[resident]

    def _form_G_r(self) -> tuple[bool, dict]:
        """
        Forms the reduced assignment graph self.G_r from self.M.

        :return double bound flag: a boolean indicating whether any resident is bound
        to more than one hospital
        :return bound residents: a map of residents to their bound hospitals.
        """
        raise NotImplementedError("Must be implemented by each algorithm.")

    def _is_under_quota_in_M_r(self, hospital):
        return (
            len(self.maximum_matching["hospitals"][hospital])
            < self.G_r[hospital]["quota"]
        )

    def _BFS(self):
        queue = deque(maxlen=len(self.hospitals))
        self.dist = {None: float("inf")}
        for h in self.hospitals:
            if self._is_under_quota_in_M_r(h):
                self.dist[h] = 0
                queue.append(h)
            else:
                self.dist[h] = float("inf")

        while queue:
            h = queue.popleft()
            if self.dist[h] < self.dist[None]:
                for r in self.G_r[h]["assigned"]:
                    target = self.maximum_matching["residents"][r]
                    if self.dist[target] == float("inf"):
                        self.dist[target] = self.dist[h] + 1
                        queue.append(target)

        return self.dist[None] != float("inf")

    def _DFS(self, h):
        if h is None:
            return True

        for r in self.G_r[h]["assigned"]:
            target = self.maximum_matching["residents"][r]
            if self.dist[target] == self.dist[h] + 1:
                if self._DFS(target):
                    self.maximum_matching["residents"][r] = h
                    self.maximum_matching["hospitals"][h].add(r)
                    return True
        self.dist[h] = float("inf")
        return False

    def _get_maximum_matching_in_G_r(self):
        """
        An extension of Hopcroft-Karp that matches Gabow 1983 for time-complexity.
        """
        self._reset_maximum_matching()
        while self._BFS():
            for h in self.hospitals:
                if self._is_under_quota_in_M_r(h):
                    self._DFS(h)

    def _select_feasible_matching(self) -> bool:
        """
        Selects a strongly stable matching where it is possible to do so.

        :return: a boolean indicating whether a stable matching was successful.
        """
        double_bound_flag, bound_residents = self._form_G_r()

        self._get_maximum_matching_in_G_r()

        for resident in self.residents:
            self.M[resident] = {"assigned": None}
        for hospital in self.hospitals:
            self.M[hospital] = {"assigned": set()}

        for r, h in bound_residents.items():
            self.M[r]["assigned"] = h
            self.M[h]["assigned"].add(r)

        for r, h in self.maximum_matching["residents"].items():
            self.M[r]["assigned"] = h
            self.M[h]["assigned"].add(r)

        if double_bound_flag:
            return False
        return True

    def _get_critical_set(self):
        """
        Finds the critical set of residents in the current maximum matching.
        """
        U_r = set()
        for r, h in self.maximum_matching["residents"].items():
            if h is None:
                U_r.add(r)

        unexplored_residents = U_r.copy()
        explored_residents = set()
        visited_hospitals = set()

        while unexplored_residents:
            r = unexplored_residents.pop()
            explored_residents.add(r)

            hospitals_to_explore = self.G_r[r]["assigned"].copy()
            matched_h = self.maximum_matching["residents"][r]
            if matched_h is not None:
                hospitals_to_explore.remove(matched_h)

            for h in hospitals_to_explore:
                if h not in visited_hospitals:
                    visited_hospitals.add(h)

                    for matched_r in self.G_r[h]["assigned"]:
                        unexplored_residents.add(matched_r)

        return explored_residents

    def _get_domination_index(self, hospital):
        capacity = self.hospitals[hospital]["capacity"]
        seen_residents = 0
        for idx, r_tie in enumerate(self._get_pref_list(hospital)):
            seen_residents += len(r_tie & self.M[hospital]["assigned"])
            if seen_residents >= capacity:
                return idx
        raise ValueError(f"Hospital {hospital} was not full or oversubscribed.")

    def _delete_dominated_residents(self, hospital):
        dom_idx = self._get_domination_index(hospital)
        for reject_tie in self._get_pref_list(hospital)[dom_idx + 1 :]:
            for reject in reject_tie.copy():
                self._break_assignment(hospital, reject)
                self._delete_pair(hospital, reject)
