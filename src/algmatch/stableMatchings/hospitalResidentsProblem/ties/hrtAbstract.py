"""
Hospital Residents Problem With Ties - Abstract class
"""

from copy import deepcopy

from algmatch.stableMatchings.hospitalResidentsProblem.ties.hrtPreferenceInstance import (
    HRTPreferenceInstance,
)
from algmatch.abstractClasses.preferenceSource import PreferenceSource
from algmatch.abstractClasses.stabilityType import StabilityType


class HRTAbstract:
    def __init__(self, source: PreferenceSource, stability_type: StabilityType) -> None:
        self._reader = HRTPreferenceInstance(source)
        self.stability_type = stability_type

        self.residents = self._reader.residents
        self.hospitals = self._reader.hospitals

        self.original_residents = deepcopy(self.residents)
        self.original_hospitals = deepcopy(self.hospitals)

        self.M = {}  # provisional matching
        self.stable_matching = {
            "resident_sided": {r: "" for r in self.residents},
            "hospital_sided": {h: set() for h in self.hospitals},
        }
        self.is_stable = False

    def _get_worst_existing_resident(self, hospital):
        existing_residents = self.M[hospital]["assigned"]

        if len(existing_residents) == 0:
            return None

        def rank_comparator(x):
            return -self.hospitals[hospital]["rank"][x]

        return min(existing_residents, key=rank_comparator)

    def _check_super_stability(self) -> bool:
        # stability must be checked with regards to the original lists prior to deletions
        for resident, r_prefs in self.original_residents.items():
            matched_hospital = self.M[resident]["assigned"]

            preferred_hospitals = r_prefs["list"]
            if matched_hospital is not None:
                rank_worst_matched_hospital = r_prefs["rank"][matched_hospital]
                # every hospital that r_i prefers to their match or is indifferent between them
                preferred_hospitals = r_prefs["list"][: rank_worst_matched_hospital + 1]

            for h_tie in preferred_hospitals:
                for hospital in h_tie:
                    if hospital == matched_hospital:
                        continue

                    if (
                        len(self.M[hospital]["assigned"])
                        < self.hospitals[hospital]["capacity"]
                    ):
                        return False

                    worst_resident = self._get_worst_existing_resident(hospital)
                    h_prefs = self.original_hospitals[hospital]
                    rank_worst = h_prefs["rank"][worst_resident]
                    rank_resident = h_prefs["rank"][resident]
                    if rank_resident <= rank_worst:
                        return False
        return True

    def _check_strong_stability(self) -> bool:
        # stability must be checked with regards to the original lists prior to deletions
        for resident, r_prefs in self.original_residents.items():
            matched_hospital = self.M[resident]["assigned"]

            if matched_hospital is not None:
                rank_worst_matched_hospital = r_prefs["rank"][matched_hospital]
                preferred_hospitals = r_prefs["list"][:rank_worst_matched_hospital]
                indifferent_hospitals = r_prefs["list"][rank_worst_matched_hospital]
            else:
                preferred_hospitals = r_prefs["list"]
                indifferent_hospitals = []

            for h_tie in preferred_hospitals:
                for hospital in h_tie:
                    if (
                        len(self.M[hospital]["assigned"])
                        < self.hospitals[hospital]["capacity"]
                    ):
                        return False

                    worst_resident = self._get_worst_existing_resident(hospital)
                    h_prefs = self.original_hospitals[hospital]
                    rank_worst = h_prefs["rank"][worst_resident]
                    rank_resident = h_prefs["rank"][resident]
                    if rank_resident <= rank_worst:
                        return False

            for hospital in indifferent_hospitals:
                if hospital == matched_hospital:
                    continue
                if (
                    len(self.M[hospital]["assigned"])
                    < self.hospitals[hospital]["capacity"]
                ):
                    return False

                worst_resident = self._get_worst_existing_resident(hospital)
                h_prefs = self.original_hospitals[hospital]
                rank_worst = h_prefs["rank"][worst_resident]
                rank_resident = h_prefs["rank"][resident]
                if rank_resident < rank_worst:
                    return False

        return True

    def _get_prefs(self, participant) -> list:
        if participant in self.residents:
            return self.residents[participant]
        elif participant in self.hospitals:
            return self.hospitals[participant]
        else:
            raise ValueError(f"{participant} is not a resident or a hospital")

    def _get_pref_list(self, participant) -> list:
        return self._get_prefs(participant)["list"]

    def _get_pref_ranks(self, participant) -> dict:
        return self._get_prefs(participant)["rank"]

    def _get_pref_length(self, person) -> int:
        pref_list = self._get_pref_list(person)
        total = sum([len(tie) for tie in pref_list])
        return total

    def _get_head(self, person) -> set:
        pref_list = self._get_pref_list(person)
        idx = 0
        while idx < len(pref_list):
            head = pref_list[idx]
            if len(head) > 0:
                return head
            idx += 1
        raise ValueError("Pref_list empty")

    def _get_tail(self, person) -> set:
        pref_list = self._get_pref_list(person)
        idx = len(pref_list) - 1
        while idx >= 0:
            tail = pref_list[idx]
            if len(tail) > 0:
                return tail
            idx -= 1
        raise ValueError("Pref_list empty")

    def _assign(self, resident, hospital) -> None:
        self.M[resident]["assigned"].add(hospital)
        self.M[hospital]["assigned"].add(resident)

    def _break_assignment(self, resident, hospital) -> None:
        self.M[resident]["assigned"].discard(hospital)
        self.M[hospital]["assigned"].discard(resident)

    def _delete_pair(self, resident, hospital) -> None:
        # allow either order of args
        if resident in self.hospitals:
            resident, hospital = hospital, resident
        # TO-DO: speed this up iusing ranks
        for tie in self.residents[resident]["list"]:
            tie.discard(hospital)
        for tie in self.hospitals[hospital]["list"]:
            tie.discard(resident)

    def _delete_tail(self, person) -> None:
        tail = self._get_tail(person)
        while len(tail) != 0:
            deletion = tail.pop()
            self._break_assignment(person, deletion)
            self._delete_pair(person, deletion)

    def _break_all_assignments(self, person) -> None:
        assignee_set = self.M[person]["assigned"]
        while len(assignee_set) != 0:
            assignee = assignee_set.pop()
            self._break_assignment(person, assignee)

    def _reject_lower_ranks(self, target, proposer) -> None:
        rank_p = self._get_pref_ranks(target)[proposer]
        for reject_tie in self._get_pref_list(target)[rank_p + 1 :]:
            while len(reject_tie) != 0:
                reject = reject_tie.pop()
                self._break_assignment(target, reject)
                self._delete_pair(target, reject)

    def _neighbourhood(self, people):
        if not people:
            return set()
        return set.union(*[self.M[person]["assigned"] for person in people])

    def _while_loop(self) -> bool:
        raise NotImplementedError("Method _while_loop must be implemented in subclass")

    def save_resident_sided(self) -> None:
        for resident in self.residents:
            hospital = self.M[resident]["assigned"]
            if hospital is None:
                self.stable_matching["resident_sided"][resident] = ""
            else:
                self.stable_matching["resident_sided"][resident] = hospital

    def save_hospital_sided(self) -> None:
        for hospital in self.hospitals:
            resident_set = self.M[hospital]["assigned"]
            if resident_set != set():
                self.stable_matching["hospital_sided"][hospital] = resident_set

    def run(self) -> None:
        if self._while_loop():
            self.save_resident_sided()
            self.save_hospital_sided()

            if self.stability_type == StabilityType.SUPER:
                self.is_stable = self._check_super_stability()
            else:
                self.is_stable = self._check_strong_stability()

            if self.is_stable:
                return f"stable matching: {self.stable_matching}"
        return "no stable matching"
