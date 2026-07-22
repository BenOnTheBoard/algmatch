"""
Store preference lists for Stable Marriage stable matching algorithm.
"""

from itertools import product

from algmatch.abstractClasses.abstractPreferenceInstanceWithTies import (
    AbstractPreferenceInstanceWithTies,
)
from algmatch.abstractClasses.preferenceSource import PreferenceSource
from algmatch.stableMatchings.stableMarriageProblem.ties.fileReader import FileReader
from algmatch.stableMatchings.stableMarriageProblem.ties.dictionaryReader import (
    DictionaryReader,
)
from algmatch.errors.InstanceSetupErrors import PrefRepError, PrefNotFoundError


class SMTPreferenceInstance(AbstractPreferenceInstanceWithTies):
    def __init__(self, source: PreferenceSource) -> None:
        super().__init__(source=source)
        self._general_setup_procedure()

    def _load(self, source: PreferenceSource) -> None:
        reader = source.build_reader(FileReader, DictionaryReader)
        self.men = reader.men
        self.women = reader.women

    def check_preference_lists(self) -> None:
        for m, m_prefs in self.men.items():
            if self.any_repetitions(m_prefs["list"]):
                raise PrefRepError("man", m)

            for w_tie in m_prefs["list"]:
                for w in w_tie:
                    if w not in self.women:
                        raise PrefNotFoundError("man", m, w)

        for w, w_prefs in self.women.items():
            if self.any_repetitions(w_prefs["list"]):
                raise PrefRepError("woman", w)

            for m_tie in w_prefs["list"]:
                for m in m_tie:
                    if m not in self.men:
                        raise PrefNotFoundError("woman", w, m)

    def clean_unacceptable_pairs(self) -> None:
        for m, w in product(self.men, self.women):
            m_list = self.men[m]["list"]
            w_list = self.women[w]["list"]

            m_found = any([m in tie for tie in w_list])
            w_found = any([w in tie for tie in m_list])

            if not (m_found and w_found):
                for tie in m_list:
                    try:
                        tie.remove(w)
                    except KeyError:
                        pass
                for tie in w_list:
                    try:
                        tie.remove(m)
                    except KeyError:
                        pass
                # clean empty sets
                # we've produced at most one per side in this loop
                if set() in m_list:
                    m_list.remove(set())
                if set() in w_list:
                    w_list.remove(set())

    def set_up_rankings(self):
        for m in self.men:
            ranking = {}
            for i, tie in enumerate(self.men[m]["list"]):
                # there are no reps, all comprehensions are disjoint
                ranking |= {woman: i for woman in tie}
            self.men[m]["rank"] = ranking

        for w in self.women:
            ranking = {}
            for i, tie in enumerate(self.women[w]["list"]):
                # there are no reps, all comprehensions are disjoint
                ranking |= {man: i for man in tie}
            self.women[w]["rank"] = ranking
