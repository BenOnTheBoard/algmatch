"""
Store preference lists for Stable Roommates stable matching algorithm.
"""

from algmatch.abstractClasses.abstractPreferenceInstance import (
    AbstractPreferenceInstance,
)
from algmatch.abstractClasses.preferenceSource import PreferenceSource
from algmatch.errors.InstanceSetupErrors import PrefSelfError
from algmatch.stableMatchings.stableRoommatesProblem.fileReader import FileReader
from algmatch.stableMatchings.stableRoommatesProblem.dictionaryReader import (
    DictionaryReader,
)


class SRPreferenceInstance(AbstractPreferenceInstance):
    def __init__(self, source: PreferenceSource) -> None:
        super().__init__(source=source)
        self._general_setup_procedure()

    def _load(self, source: PreferenceSource) -> None:
        reader = source.build_reader(FileReader, DictionaryReader)
        self.roommates = reader.roommates

    def check_preference_lists(self) -> None:
        self.check_preferences_single_group(self.roommates, "roommate", self.roommates)
        for r, prefs in self.roommates.items():
            if r in prefs["list"]:
                raise PrefSelfError("roommate", r)

    def clean_unacceptable_pairs(self) -> None:
        super().clean_unacceptable_pairs(self.roommates, self.roommates)

    def set_up_rankings(self) -> None:
        self.tieless_lists_to_rank(self.roommates)
