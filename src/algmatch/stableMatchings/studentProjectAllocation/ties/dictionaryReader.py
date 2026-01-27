"""
Class to read in a dictionary of preferences for the SPAST stable matching algorithms.
"""

from algmatch.abstractClasses.abstractReader import AbstractReader
from algmatch.errors.ReaderErrors import (
    CapacityError,
    IDMisformatError,
    RepeatIDError,
    PrefListMisformatError,
    OffererError,
)


class DictionaryReader(AbstractReader):
    def __init__(self, dictionary: dict) -> None:
        super().__init__(dictionary)
        self._read_data()

    def _read_data(self) -> None:
        self.students = {}
        self.projects = {}
        self.lecturers = {}

        for key, value in self.data.items():
            match key:
                case "students":
                    for k, v in value.items():
                        if type(k) is not int:
                            raise IDMisformatError("student", k)
                        student = f"s{k}"
                        if student in self.students:
                            raise RepeatIDError("student", k)

                        for i in v:
                            # if not int, must be a tie list
                            if type(i) is not int and not all(
                                type(j) is int for j in i
                            ):
                                raise PrefListMisformatError("student", k, i)

                        preferences = []
                        for i, elt in enumerate(v):
                            if isinstance(elt, int):
                                tie = set()
                                tie.add(f"p{elt}")
                            else:
                                tie = {f"p{j}" for j in elt}
                            preferences.append(tie)

                        self.students[student] = {"list": preferences, "rank": dict()}

                case "projects":
                    for k, v in value.items():
                        if type(k) is not int:
                            raise IDMisformatError("project", k)
                        project = f"p{k}"
                        if project in self.projects:
                            raise RepeatIDError("project", k)

                        if type(v["capacity"]) is not int:
                            raise CapacityError("project", k)
                        capacity = v["capacity"]

                        if type(v["lecturer"]) is not int:
                            raise OffererError("project", "lecturer", k)
                        offerer = f"l{v['lecturer']}"

                        self.projects[project] = {
                            "capacity": capacity,
                            "lecturer": offerer,
                        }

                case "lecturers":
                    for k, v in value.items():
                        if type(k) is not int:
                            raise IDMisformatError("lecturer", k)
                        lecturer = f"l{k}"
                        if lecturer in self.lecturers:
                            raise RepeatIDError("lecturer", k)

                        if type(v["capacity"]) is not int:
                            raise CapacityError("lecturer", k)
                        capacity = v["capacity"]

                        for i in v["preferences"]:
                            # if not int, must be a tie list
                            if type(i) is not int and not all(
                                type(j) is int for j in i
                            ):
                                raise PrefListMisformatError("lecturer", k, i)

                        preferences = []
                        for i, elt in enumerate(v["preferences"]):
                            if isinstance(elt, int):
                                tie = set()
                                tie.add(f"s{elt}")
                            else:
                                tie = {f"s{j}" for j in elt}
                            preferences.append(tie)

                        self.lecturers[lecturer] = {
                            "capacity": capacity,
                            "projects": set(),
                            "list": preferences,
                            "rank": dict(),
                        }
