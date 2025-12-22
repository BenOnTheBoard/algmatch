"""
Algorithm to produce M_0, the hospital-optimal, resident-pessimal strongly stable matching, where such a thing exists.
"""

from algmatch.stableMatchings.hospitalResidentsProblem.ties.hrtStrongAbstract import (
    HRTStrongAbstract,
)


class HRTStrongHospitalOptimal(HRTStrongAbstract):
    def __init__(self, filename=None, dictionary=None):
        super().__init__(filename=filename, dictionary=dictionary)

        self.undersub_hospitals = set()

        self.unbound = {h: set() for h in self.hospitals}

        for resident in self.residents:
            self.M[resident] = {"assigned": set()}

        for hospital, h_prefs in self.hospitals.items():
            if len(h_prefs["list"]) > 0:
                self.undersub_hospitals.add(hospital)
            self.M[hospital] = {"assigned": set()}

    def _get_worst_assignees(self, hospital) -> set:
        assignees = self.M[hospital]["assigned"]
        pref_list = self._get_pref_list(hospital)
        for r_tie in pref_list[::-1]:
            assigned_in_tie = r_tie & assignees
            if assigned_in_tie:
                return assigned_in_tie
        raise ValueError("Not assigned anything in preference list.")

    def _assign(self, resident, hospital) -> None:
        super()._assign(resident, hospital)
        if resident in self.hospitals:
            resident, hospital = hospital, resident

        capacity = self.hospitals[hospital]["capacity"]
        occupancy = len(self.M[hospital]["assigned"])
        if occupancy >= capacity:
            self.undersub_hospitals.discard(hospital)
        if occupancy > capacity:
            self.unbound[hospital] = self._get_worst_assignees(hospital)

    def _break_assignment(self, resident, hospital):
        super()._break_assignment(resident, hospital)
        if resident in self.hospitals:
            resident, hospital = hospital, resident

        capacity = self.hospitals[hospital]["capacity"]
        occupancy = len(self.M[hospital]["assigned"])
        if occupancy < capacity:
            self.undersub_hospitals.add(hospital)
        if occupancy <= capacity:
            self.unbound[hospital] = set()

    def _get_next_residents(self, h):
        pref_list = self._get_pref_list(h)
        current_residents = self.M[h]["assigned"]
        idx = 0
        while idx < len(pref_list):
            head = pref_list[idx]
            remaining_head = head - current_residents
            if remaining_head:
                return remaining_head
            idx += 1
        return None

    def _form_G_r(self):
        self._reset_G_r()
        bound_residents = dict()

        for h in self.hospitals:
            bound_assignees = self.M[h]["assigned"] - self.unbound[h]
            for r in bound_assignees:
                bound_residents[r] = h
            self.G_r[h]["quota"] -= len(bound_assignees)

        for r in bound_residents:
            self._remove_from_G_r(r)

        for r in self.residents:
            if len(self.M[r]["assigned"]) == 0:
                self._remove_from_G_r(r)

        # As opposed to the resident-oriented algorithm,
        # we know that there are no double-bound residents.
        return False, bound_residents

    def _double_bound_deletions(self):
        made_deletion = True
        while made_deletion:
            made_deletion = False
            for r in self.residents:
                seen_bound = False
                for h in self.M[r]["assigned"]:
                    if r not in self.unbound[h]:
                        if seen_bound:
                            made_deletion = True
                            self._delete_tail(r)
                            break
                        else:
                            seen_bound = True

    def _while_loop(self):
        C = {None}
        while C:
            while len(self.undersub_hospitals) != 0:
                h = next(iter(self.undersub_hospitals))
                r_tie = self._get_next_residents(h)

                if r_tie is None:
                    self.undersub_hospitals.discard(h)
                    continue

                for r in r_tie.copy():
                    self._assign(r, h)
                    self._reject_lower_ranks(r, h)

                self._double_bound_deletions()

            self._form_G_r()
            self._get_maximum_matching_in_G_r()
            C = self._get_critical_set()
            for r in C:
                self._delete_tail(r)
            self._double_bound_deletions()

        self._select_feasible_matching()

        for h in self.hospitals:
            h_assignees = self.M[h]["assigned"]
            occupancy = len(h_assignees)
            capacity = self.hospitals[h]["capacity"]

            # Sandy Scott Thesis Lemma 2.4.2.
            if occupancy < capacity:
                for r_tie in self._get_pref_list(h):
                    for r in r_tie:
                        if r not in h_assignees:
                            return False

        return True
