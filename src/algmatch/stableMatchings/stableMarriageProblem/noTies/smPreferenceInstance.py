"""
Store preference lists for Stable Marriage stable matching algorithm.
"""

from algmatch.abstractClasses.abstractPreferenceInstance import (
    AbstractPreferenceInstance,
)
from algmatch.abstractClasses.preferenceSource import PreferenceSource
from algmatch.stableMatchings.stableMarriageProblem.noTies.fileReader import FileReader
from algmatch.stableMatchings.stableMarriageProblem.noTies.dictionaryReader import (
    DictionaryReader,
)


class SMPreferenceInstance(AbstractPreferenceInstance):
    def __init__(self, source: PreferenceSource) -> None:
        super().__init__(source=source)
        self._general_setup_procedure()

    def _load(self, source: PreferenceSource) -> None:
        reader = source.build_reader(FileReader, DictionaryReader)
        self.men = reader.men
        self.women = reader.women

    def check_preference_lists(self) -> None:
        self.check_preferences_single_group(self.men, "man", self.women)
        self.check_preferences_single_group(self.women, "woman", self.men)

    def clean_unacceptable_pairs(self) -> None:
        super().clean_unacceptable_pairs(self.men, self.women)

    def set_up_rankings(self) -> None:
        self.tieless_lists_to_rank(self.men)
        self.tieless_lists_to_rank(self.women)
