"""
Class to provide interface for the Student Project Allocation stable matching algorithm.

:param filename: str, optional, default=None, the path to the file to read in the preferences from.
:param dictionary: dict, optional, default=None, the dictionary of preferences.
:param optimised_side: str, optional, default="student", whether the algorithm is "student" (default) or "lecturer" sided.
"""

from algmatch.stableMatchings.studentProjectAllocation.noTies.spaStudentOptimal import (
    SPAStudentOptimal,
)
from algmatch.stableMatchings.studentProjectAllocation.noTies.spaLecturerOptimal import (
    SPALecturerOptimal,
)
from algmatch.abstractClasses.preferenceSource import PreferenceSource


class StudentProjectAllocation:
    def __init__(
        self,
        filename: str | None = None,
        dictionary: dict | None = None,
        optimised_side: str = "student",
    ) -> None:
        """
        Initialise the Student Project Allocation algorithm.

        :param filename: str, optional, default=None, the path to the file to read in the preferences from.
        :param dictionary: dict, optional, default=None, the dictionary of preferences.
        :param optimised_side: str, optional, default="student", whether the algorithm is "student" (default) or "lecturer" sided.
        """
        self.source = PreferenceSource(filename=filename, dictionary=dictionary)

        assert type(optimised_side) is str, "Param optimised_side must be of type str"
        optimised_side = optimised_side.lower()
        assert optimised_side in ("students", "lecturers"), (
            "optimised_side must be either 'students' or 'lecturers'"
        )

        if optimised_side == "students":
            self.spa_alg = SPAStudentOptimal(source=self.source)
        else:
            self.spa_alg = SPALecturerOptimal(source=self.source)

    def get_stable_matching(self) -> dict | None:
        """
        Get the stable matching for the Student Project Allocation algorithm.

        :return: dict, the stable matching.
        """
        self.spa_alg.run()
        if self.spa_alg.is_stable:
            return self.spa_alg.stable_matching
        return None
