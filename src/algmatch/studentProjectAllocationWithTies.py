"""
Class to provide interface for the Student Project Allocation With Ties algorithms.
"""

import os

from algmatch.stableMatchings.studentProjectAllocation.ties.spastSuperStudentOptimal import (
    SPASTSuperStudentOptimal,
)
from algmatch.stableMatchings.studentProjectAllocation.ties.spastAbstract import (
    SPASTAbstract,
)


class StudentProjectAllocationWithTies:
    def __init__(
        self,
        filename: str | None = None,
        dictionary: dict | None = None,
        optimised_side: str = "students",
        stability_type: str = None,
    ) -> None:
        """
        Initialise the Student Project Allocation Problem With Ties algorithms.
        :param filename: str, optional, default=None, the path to the file to read in the preferences from.
        :param dictionary: dict, optional, default=None, the dictionary of preferences.
        :param optimised_side: str, optional, default="students", whether the algorithm is "students" (default) or "lecturers" sided.
        :param stability_type: str, default=None, specifies the stability condition to be solved for.
        """

        if filename is not None:
            filename = os.path.join(os.getcwd(), filename)

        self._validate_and_save_parameters(
            filename, dictionary, optimised_side, stability_type
        )
        self._set_algorithm()

    def _assert_valid_optimised_side(self, optimised_side):
        assert type(optimised_side) is str, "Param optimised_side must be of type str"
        optimised_side = optimised_side.lower()
        assert optimised_side in ("students", "lecturers"), (
            "Optimised side must either be 'students' or 'lecturers'"
        )

    def _validate_and_save_parameters(
        self, filename, dictionary, optimised_side, stability_type
    ):
        self._assert_valid_optimised_side(optimised_side)
        self.optimised_side = optimised_side.lower()

        SPASTAbstract._assert_valid_stability_type(stability_type)
        self.stability_type = stability_type.lower()

        self.filename = filename
        self.dictionary = dictionary

    def _set_algorithm(self):
        if self.stability_type == "super":
            if self.optimised_side == "students":
                self.spas_alg = SPASTSuperStudentOptimal(
                    filename=self.filename, dictionary=self.dictionary
                )
            else:
                raise NotImplementedError(
                    "Lecturer oriented algorithms are not yet available."
                )
        elif self.stability_type == "strong":
            raise NotImplementedError("Strong algorithms are not yet available.")
        else:
            raise ValueError('stability_type must be either "strong" or "super".')

    def get_stable_matching(self) -> dict | None:
        """
        Get the stable matching for the Student Project Allocation Problem With Ties algorithm.

        :return: dict, the stable matching for this instance
        """
        self.spas_alg.run()
        if self.spas_alg.is_stable:
            return self.spas_alg.stable_matching
        return None
