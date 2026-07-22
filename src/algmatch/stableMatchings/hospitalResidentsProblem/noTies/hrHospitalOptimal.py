"""
Algorithm to produce the resident-optimal, hospital-pessimal stable matching.
"""

from algmatch.stableMatchings.hospitalResidentsProblem.noTies.hrAbstract import (
    HRAbstract,
)
from algmatch.abstractClasses.preferenceSource import PreferenceSource


class HRHospitalOptimal(HRAbstract):
    def __init__(self, source: PreferenceSource) -> None:
        super().__init__(source)
        self.undersub_hospitals = set()

        for resident in self.residents:
            self.M[resident] = {"assigned": None}

        for hospital, prefs in self.hospitals.items():
            if len(prefs["list"]) > 0:
                self.undersub_hospitals.add(hospital)
            self.M[hospital] = {"assigned": set()}

    def _assign_pair(self, resident, hospital):
        self.M[resident]["assigned"] = hospital
        self.M[hospital]["assigned"].add(resident)

    def _delete_pair(self, resident, hospital):
        self.residents[resident]["list"].remove(hospital)
        self.hospitals[hospital]["list"].remove(resident)
        if len(self.hospitals[hospital]["list"]) == 0:
            self.undersub_hospitals.discard(hospital)

    def _break_assignment(self, resident, hospital):
        self.M[resident]["assigned"] = None
        self.M[hospital]["assigned"].remove(resident)
        if self.get_first_unassigned_resident(hospital) is not None:
            self.undersub_hospitals.add(hospital)

    def get_first_unassigned_resident(self, hospital):
        for resident in self.hospitals[hospital]["list"]:
            if resident not in self.M[hospital]["assigned"]:
                return resident
        return None

    def _while_loop(self):
        while len(self.undersub_hospitals) != 0:
            h = self.undersub_hospitals.pop()
            r = self.get_first_unassigned_resident(h)

            occupancy = len(self.M[h]["assigned"])

            while r is not None and occupancy < self.hospitals[h]["capacity"]:
                h_prime = self.M[r]["assigned"]

                if h_prime is not None:
                    self._break_assignment(r, h_prime)
                self._assign_pair(r, h)

                rank_h = self.residents[r]["rank"][h]
                for reject in self.residents[r]["list"][rank_h + 1 :]:
                    self._delete_pair(r, reject)

                # See if the hospital can make another offer
                # If yes, loop. If no, next hospital.
                occupancy += 1
                r = self.get_first_unassigned_resident(h)
