"""
Hospital/Residents Problem - Abstract class
"""

from copy import deepcopy
import os

from algmatch.stableMatchings.hospitalResidentsProblem.noTies.hrPreferenceInstance import (
    HRPreferenceInstance,
)


class HRAbstract:
    def __init__(
        self, filename: str | None = None, dictionary: dict | None = None
    ) -> None:
        assert filename is not None or dictionary is not None, (
            "Either filename or dictionary must be provided"
        )
        assert not (filename is not None and dictionary is not None), (
            "Only one of filename or dictionary must be provided"
        )

        if filename is not None:
            assert os.path.isfile(filename), f"File {filename} does not exist"
            self._reader = HRPreferenceInstance(filename=filename)

        if dictionary is not None:
            self._reader = HRPreferenceInstance(dictionary=dictionary)

        self.residents = self._reader.residents
        self.hospitals = self._reader.hospitals

        # we need original copies of the preference lists to check the stability of solutions
        self.original_residents = deepcopy(self.residents)
        self.original_hospitals = deepcopy(self.hospitals)

        self.M = {}  # provisional matching
        self.stable_matching = {
            "resident_sided": {resident: "" for resident in self.residents},
            "hospital_sided": {hospital: set() for hospital in self.hospitals},
        }
        self.is_stable = False

    def _blocking_pair_condition(self, resident, hospital):
        h_info = self.original_hospitals[hospital]
        assignees = self.M[hospital]["assigned"]

        cj = h_info["capacity"]
        occupancy = len(assignees)
        if occupancy < cj:
            return True

        resident_rank = h_info["rank"][resident]
        for existing_resident in assignees:
            existing_rank = h_info["rank"][existing_resident]
            if resident_rank < existing_rank:
                return True

        return False

    def _check_stability(self):
        # stability must be checked with regards to the original lists prior to deletions
        for resident, r_prefs in self.original_residents.items():
            preferred_hospitals = r_prefs["list"]
            if self.M[resident]["assigned"] is not None:
                matched_hospital = self.M[resident]["assigned"]
                rank_matched_hospital = r_prefs["rank"][matched_hospital]
                preferred_hospitals = r_prefs["list"][:rank_matched_hospital]

            for hospital in preferred_hospitals:
                if self._blocking_pair_condition(resident, hospital):
                    return False

        return True

    def _while_loop(self):
        raise NotImplementedError("Method _while_loop must be implemented in subclass")

    def run(self) -> None:
        self._while_loop()

        for resident in self.residents:
            hospital = self.M[resident]["assigned"]
            if hospital is not None:
                self.stable_matching["resident_sided"][resident] = hospital
                self.stable_matching["hospital_sided"][hospital].add(resident)

        self.is_stable = self._check_stability()

        if self.is_stable:
            return f"stable matching: {self.stable_matching}"
        else:
            return f"unstable matching: {self.stable_matching}"
