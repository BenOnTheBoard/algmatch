"""
Stable Marriage Problem - Abstract class
"""

from copy import deepcopy
import os

from algmatch.stableMatchings.stableMarriageProblem.noTies.smPreferenceInstance import (
    SMPreferenceInstance,
)


class SMAbstract:
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
            self._reader = SMPreferenceInstance(filename=filename)

        if dictionary is not None:
            self._reader = SMPreferenceInstance(dictionary=dictionary)

        self.men = self._reader.men
        self.women = self._reader.women

        self.original_men = deepcopy(self.men)
        self.original_women = deepcopy(self.women)

        self.M = {}  # provisional matching
        self.stable_matching = {
            "man_sided": {m: "" for m in self.men},
            "woman_sided": {w: "" for w in self.women},
        }
        self.is_stable = False

    def _check_stability(self):
        # stability must be checked with regards to the original lists prior to deletions
        for man, m_prefs in self.original_men.items():
            preferred_women = m_prefs["list"]
            if self.M[man]["assigned"] is not None:
                matched_woman = self.M[man]["assigned"]
                rank_matched_woman = m_prefs["rank"][matched_woman]
                # every woman that m_i prefers to his matched partner
                preferred_women = m_prefs["list"][:rank_matched_woman]

            for woman in preferred_women:
                existing_fiance = self.M[woman]["assigned"]
                if existing_fiance is None:
                    return False
                else:
                    w_ranks = self.original_women[woman]["rank"]
                    rank_fiance = w_ranks[existing_fiance]
                    rank_man = w_ranks[man]
                    if rank_man < rank_fiance:
                        return False

        return True

    def _while_loop(self):
        raise NotImplementedError("Method _while_loop must be implemented in subclass")

    def run(self) -> None:
        self._while_loop()

        for man in self.men:
            woman = self.M[man]["assigned"]
            if woman is not None:
                self.stable_matching["man_sided"][man] = woman
                self.stable_matching["woman_sided"][woman] = man

        self.is_stable = self._check_stability()

        if self.is_stable:
            return f"stable matching: {self.stable_matching}"
        else:
            return f"unstable matching: {self.stable_matching}"
