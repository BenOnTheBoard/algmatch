"""
Algorithm to produce M_0, the resident-optimal, hospital-pessimal strongly stable matching, where such a thing exists.
"""

from algmatch.stableMatchings.hospitalResidentsProblem.ties.hrtStrongAbstract import (
    HRTStrongAbstract,
)


class HRTStrongResidentOptimal(HRTStrongAbstract):
    def __init__(
        self, filename: str | None = None, dictionary: dict | None = None
    ) -> None:
        super().__init__(filename=filename, dictionary=dictionary)

        self.unassigned_residents = set()
        self.been_full = {h: False for h in self.hospitals}

        for resident, r_prefs in self.residents.items():
            if len(r_prefs["list"]) > 0:
                self.unassigned_residents.add(resident)
            self.M[resident] = {"assigned": set()}

        for hospital in self.hospitals:
            self.M[hospital] = {"assigned": set()}

    def _delete_pair(self, resident, hospital):
        super()._delete_pair(resident, hospital)
        if resident in self.hospitals:
            resident, hospital = hospital, resident
        if self._get_pref_length(resident) == 0:
            self.unassigned_residents.discard(resident)

    def _break_assignment(self, resident, hospital):
        super()._break_assignment(resident, hospital)
        if resident in self.hospitals:
            resident, hospital = hospital, resident
        if self._get_pref_length(resident) > 0:
            self.unassigned_residents.add(resident)

    def _form_G_r(self):
        self._reset_G_r()
        found_double_bound_resident = False
        bound_residents = dict()

        for h in self.hospitals:
            capacity = self.hospitals[h]["capacity"]
            occupancy = len(self.M[h]["assigned"])
            if occupancy <= capacity:
                for r in self.G_r[h]["assigned"].copy():
                    if r in bound_residents:
                        found_double_bound_resident = True
                    else:
                        bound_residents[r] = h
                    self.G_r[h]["quota"] -= 1

            else:
                h_tail = self._get_tail(h)
                for r in self.G_r[h]["assigned"] - h_tail:
                    if r in bound_residents:
                        found_double_bound_resident = True
                    else:
                        bound_residents[r] = h
                    self.G_r[h]["quota"] -= 1

        for r in bound_residents:
            self._remove_from_G_r(r)

        for r in self.residents:
            if len(self.M[r]["assigned"]) == 0:
                self._remove_from_G_r(r)

        return found_double_bound_resident, bound_residents

    def _while_loop(self) -> bool:
        Z = {None}
        while Z:
            while len(self.unassigned_residents) != 0:
                r = self.unassigned_residents.pop()
                h_tie = self._get_head(r)
                for h in h_tie.copy():
                    self._assign(r, h)

                    capacity = self.hospitals[h]["capacity"]
                    occupancy = len(self.M[h]["assigned"])
                    if occupancy >= capacity:
                        self.been_full[h] = True
                        self._delete_dominated_residents(h)

            self._form_G_r()
            self._get_maximum_matching_in_G_r()
            Z = self._get_critical_set()
            for h in self._neighbourhood(Z):
                self._delete_tail(h)

        provisional_assignee_count = {
            h: len(self.M[h]["assigned"]) for h in self.hospitals
        }

        is_successful_matching = self._select_feasible_matching()

        if not is_successful_matching:
            return False

        for h in self.hospitals:
            occupancy = len(self.M[h]["assigned"])
            # Sandy Scott Thesis Lemma 2.2.3.
            # a)
            if not self.been_full[h]:
                if occupancy < provisional_assignee_count[h]:
                    return False
            # b)
            else:
                capacity = self.hospitals[h]["capacity"]
                if capacity != occupancy:
                    return False

        return True
