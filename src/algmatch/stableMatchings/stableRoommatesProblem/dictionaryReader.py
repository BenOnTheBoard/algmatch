"""
Class to read in a file of preferences for the Stable Roomates Problem stable matching algorithm.
"""

from algmatch.abstractClasses.abstractReader import AbstractReader
from algmatch.errors.ReaderErrors import (
    IDMisformatError,
    RepeatIDError,
    PrefListMisformatError,
)


class DictionaryReader(AbstractReader):
    def __init__(self, dictionary: dict) -> None:
        super().__init__(dictionary)
        self._read_data()

    def _read_data(self) -> None:
        self.roommates = {}

        for k, v in self.data.items():
            if type(k) is not int:
                raise IDMisformatError("roommate", k)
            roommate = f"r{k}"
            if roommate in self.roommates:
                raise RepeatIDError("roommate", k)

            for i in v:
                if type(i) is not int:
                    raise PrefListMisformatError("roommate", k, i)
            preferences = [f"r{i}" for i in v]

            self.roommates[roommate] = {"list": preferences, "rank": {}}
