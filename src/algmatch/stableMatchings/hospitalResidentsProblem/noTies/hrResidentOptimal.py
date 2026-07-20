"""
Algorithm to produce the resident-optimal, hospital-pessimal stable matching.
"""

from algmatch.stableMatchings.hospitalResidentsProblem.noTies.hrAbstract import (
    HRAbstract,
)
from algmatch.abstractClasses.preferenceSource import PreferenceSource


class HRResidentOptimal(HRAbstract):
    def __init__(self, source: PreferenceSource) -> None:
        super().__init__(source)
        self.unassigned_residents = set()

        for resident, prefs in self.residents.items():
            if len(prefs["list"]) > 0:
                self.unassigned_residents.add(resident)
            self.M[resident] = {"assigned": None}

        for hospital in self.hospitals:
            self.M[hospital] = {"assigned": set()}

    def _assign_pair(self, resident, hospital):
        self.M[resident]["assigned"] = hospital
        self.M[hospital]["assigned"].add(resident)

    def _delete_pair(self, resident, hospital):
        self.residents[resident]["list"].remove(hospital)
        self.hospitals[hospital]["list"].remove(resident)
        if len(self.residents[resident]["list"]) == 0:
            self.unassigned_residents.discard(resident)

    def _break_assignment(self, resident, hospital):
        self.M[resident]["assigned"] = None
        self.M[hospital]["assigned"].remove(resident)
        if len(self.residents[resident]["list"]) > 0:
            self.unassigned_residents.add(resident)

    def _get_worst_existing_resident(self, hospital):
        existing_residents = self.M[hospital]["assigned"]

        def rank_comparator(x):
            return -self.hospitals[hospital]["rank"][x]

        worst_resident = min(existing_residents, key=rank_comparator)

        return worst_resident

    def _while_loop(self):
        while len(self.unassigned_residents) != 0:
            r = self.unassigned_residents.pop()
            h = self.residents[r]["list"][0]

            self._assign_pair(r, h)

            capacity = self.hospitals[h]["capacity"]
            occupancy = len(self.M[h]["assigned"])

            if occupancy > capacity:
                r_worst = self._get_worst_existing_resident(h)
                self._break_assignment(r_worst, h)
                occupancy -= 1

            if occupancy == capacity:
                r_worst = self._get_worst_existing_resident(h)
                rank_worst = self.hospitals[h]["rank"][r_worst]
                for reject in self.hospitals[h]["list"][rank_worst:]:
                    self._delete_pair(reject, h)
