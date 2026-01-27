"""
Algorithm to produce M_0, the hospital-optimal, resident-pessimal super-stable matching, where such a thing exists.
"""

from algmatch.stableMatchings.hospitalResidentsProblem.ties.hrtAbstract import (
    HRTAbstract,
)


class HRTSuperHospitalOptimal(HRTAbstract):
    def __init__(
        self, filename: str | None = None, dictionary: dict | None = None
    ) -> None:
        super().__init__(
            filename=filename, dictionary=dictionary, stability_type="super"
        )

        self.undersub_hospitals = set()
        self.been_assigned = {r: False for r in self.residents}

        for resident in self.residents:
            self.M[resident] = {"assigned": set()}

        for hospital, h_prefs in self.hospitals.items():
            if len(h_prefs["list"]) > 0:
                self.undersub_hospitals.add(hospital)
            self.M[hospital] = {"assigned": set()}

    def _assign(self, resident, hospital) -> None:
        super()._assign(resident, hospital)
        if resident in self.hospitals:
            resident, hospital = hospital, resident

        capacity = self.hospitals[hospital]["capacity"]
        occupancy = len(self.M[hospital]["assigned"])
        if occupancy >= capacity:
            self.undersub_hospitals.discard(hospital)

    def _break_assignment(self, resident, hospital):
        super()._break_assignment(resident, hospital)
        if resident in self.hospitals:
            resident, hospital = hospital, resident

        capacity = self.hospitals[hospital]["capacity"]
        occupancy = len(self.M[hospital]["assigned"])
        if occupancy < capacity:
            self.undersub_hospitals.add(hospital)

    def _indifferent_between_assigned_hospitals(self, r):
        r_ranks = self._get_pref_ranks(r)
        return len(set(r_ranks[h] for h in self.M[r]["assigned"])) == 1

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

    def _while_loop(self) -> bool:
        while len(self.undersub_hospitals) != 0:
            h = next(iter(self.undersub_hospitals))
            r_tie = self._get_next_residents(h)

            if r_tie is None:
                self.undersub_hospitals.discard(h)
                continue

            for r in r_tie.copy():
                self._assign(r, h)
                self.been_assigned[r] = True

                if len(
                    self.M[r]["assigned"]
                ) > 1 and self._indifferent_between_assigned_hospitals(r):
                    self._delete_tail(r)
                else:
                    self._reject_lower_ranks(r, h)

        # Check Viability of Matching
        for r in self.residents:
            if len(self.M[r]["assigned"]) > 1:
                return False
            if len(self.M[r]["assigned"]) == 0 and self.been_assigned[r]:
                return False

        for h in self.hospitals:
            capacity = self.hospitals[h]["capacity"]
            occupancy = len(self.M[h]["assigned"])
            if occupancy > capacity:
                return False

        for r in self.residents:
            if not self.M[r]["assigned"]:
                self.M[r]["assigned"] = None
            else:
                # unpack single element
                self.M[r]["assigned"] = next(iter(self.M[r]["assigned"]))

        return True
