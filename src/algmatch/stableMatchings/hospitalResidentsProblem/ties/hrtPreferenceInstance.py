"""
Store preference lists for Hospital Residents stable matching algorithm.
"""

from itertools import product

from algmatch.abstractClasses.abstractPreferenceInstanceWithTies import (
    AbstractPreferenceInstanceWithTies,
)
from algmatch.abstractClasses.preferenceSource import PreferenceSource
from algmatch.stableMatchings.hospitalResidentsProblem.ties.fileReader import FileReader
from algmatch.stableMatchings.hospitalResidentsProblem.ties.dictionaryReader import (
    DictionaryReader,
)
from algmatch.errors.InstanceSetupErrors import PrefRepError, PrefNotFoundError


class HRTPreferenceInstance(AbstractPreferenceInstanceWithTies):
    def __init__(self, source: PreferenceSource) -> None:
        super().__init__(source=source)
        self._general_setup_procedure()

    def _load(self, source: PreferenceSource) -> None:
        reader = source.build_reader(FileReader, DictionaryReader)
        self.residents = reader.residents
        self.hospitals = reader.hospitals

    def check_preference_lists(self) -> None:
        for r, r_prefs in self.residents.items():
            if self.any_repetitions(r_prefs["list"]):
                raise PrefRepError("resident", r)

            for h_tie in r_prefs["list"]:
                for h in h_tie:
                    if h not in self.hospitals:
                        raise PrefNotFoundError("resident", r, h)

        for h, h_prefs in self.hospitals.items():
            if self.any_repetitions(h_prefs["list"]):
                raise PrefRepError("hospital", h)

            for r_tie in h_prefs["list"]:
                for r in r_tie:
                    if r not in self.residents:
                        raise PrefNotFoundError("hospital", h, r)

    def clean_unacceptable_pairs(self) -> None:
        for r, h in product(self.residents, self.hospitals):
            r_list = self.residents[r]["list"]
            h_list = self.hospitals[h]["list"]

            r_found = any([r in tie for tie in h_list])
            h_found = any([h in tie for tie in r_list])

            if not (r_found and h_found):
                for tie in r_list:
                    try:
                        tie.remove(h)
                    except KeyError:
                        pass
                for tie in h_list:
                    try:
                        tie.remove(r)
                    except KeyError:
                        pass
                # clean empty sets
                # we've produced at most one per side in this loop
                if set() in r_list:
                    r_list.remove(set())
                if set() in h_list:
                    h_list.remove(set())

    def set_up_rankings(self):
        for r in self.residents:
            ranking = {}
            for i, tie in enumerate(self.residents[r]["list"]):
                # there are no reps, all comprehensions are disjoint
                ranking |= {hospital: i for hospital in tie}
            self.residents[r]["rank"] = ranking

        for h in self.hospitals:
            ranking = {}
            for i, tie in enumerate(self.hospitals[h]["list"]):
                # there are no reps, all comprehensions are disjoint
                ranking |= {resident: i for resident in tie}
            self.hospitals[h]["rank"] = ranking
