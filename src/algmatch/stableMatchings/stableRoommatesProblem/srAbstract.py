"""
Stable Roommates Problem - Abstract class
"""

from copy import deepcopy

from algmatch.stableMatchings.stableRoommatesProblem.srPreferenceInstance import (
    SRPreferenceInstance,
)
from algmatch.abstractClasses.preferenceSource import PreferenceSource


class SRAbstract:
    def __init__(self, source: PreferenceSource) -> None:
        self._reader = SRPreferenceInstance(source=source)

        self.roommates = self._reader.roommates
        self.original_roommates = deepcopy(self.roommates)

        self.M = {}  # provisional matching
        self.stable_matching = {r: "" for r in self.roommates}
        self.is_stable = False

    def _check_stability(self):
        # stability must be checked with regards to the original lists prior to deletions
        for roommate, r_prefs in self.original_roommates.items():
            preferred_partners = r_prefs["list"]
            if self.M[roommate]["assigned"] is not None:
                matched_partner = self.M[roommate]["assigned"]
                rank_matched_partner = r_prefs["rank"][matched_partner]
                # every other roomate that r_i prefers to his matched partner
                preferred_partners = r_prefs["list"][:rank_matched_partner]
            else:
                return False

            for partner in preferred_partners:
                existing_roommate = self.M[partner]["assigned"]
                if existing_roommate is None:
                    return False
                else:
                    p_ranks = self.original_roommates[partner]["rank"]
                    rank_existing_roommate = p_ranks[existing_roommate]
                    rank_roommate = p_ranks[roommate]
                    if rank_roommate < rank_existing_roommate:
                        return False

        return True

    def _while_loop(self):
        raise NotImplementedError("Method _while_loop must be implemented in subclass")

    def run(self):
        self._while_loop()

        for roommate in self.roommates:
            partner = self.M[roommate]["assigned"]
            if partner is not None:
                self.stable_matching[roommate] = partner
                self.stable_matching[partner] = roommate

        self.is_stable = self._check_stability()

        if self.is_stable:
            return f"stable matching: {self.stable_matching}"
        else:
            return f"unstable matching: {self.stable_matching}"
