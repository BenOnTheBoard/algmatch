from dataclasses import dataclass
from typing import Optional, Dict, Any, Type
import os

from algmatch.abstractClasses.abstractReader import AbstractReader


@dataclass
class PreferenceSource:
    """
    Unified representation of preference input for files and dictionaries.
    Exactly one of filename or dictionary must be non-None.
    """

    filename: Optional[str] = None
    dictionary: Optional[Dict[str, Dict[int, Any]]] = None

    def __post_init__(self):
        if (self.filename is None) == (self.dictionary is None):
            raise ValueError("Exactly one of filename or dictionary must be provided")
        if self.filename is not None:
            self.filename = os.path.join(os.getcwd(), self.filename)
            assert os.path.isfile(self.filename), f"File {self.filename} does not exist"

    def build_reader(
        self,
        file_reader_class: Type[AbstractReader],
        dict_reader_class: Type[AbstractReader],
    ) -> AbstractReader:
        if self.filename is not None:
            return file_reader_class(self.filename)
        return dict_reader_class(self.dictionary)
