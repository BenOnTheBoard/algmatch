"""
Class to provide interface for the Student Project Allocation With Ties algorithms.
"""

import os

from algmatch.stableMatchings.studentProjectAllocation.ties.spastSuperStudentOptimal import (
    SPASTSuperStudentOptimal,
)

from algmatch.abstractClasses.stabilityType import StabilityType


class StudentProjectAllocationWithTies:  #
    algorithms = {
        (StabilityType.SUPER, "students"): SPASTSuperStudentOptimal,
    }

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
        self.stability_type = StabilityType.from_value(stability_type)
        self.filename = filename
        self.dictionary = dictionary

    def _set_algorithm(self):
        alg_key = (self.stability_type, self.optimised_side)
        if alg_key not in self.algorithms:
            raise NotImplementedError(
                "No algorithm has been implemented for this case."
            )
        alg_class = self.algorithms[alg_key]
        self.spas_alg = alg_class(filename=self.filename, dictionary=self.dictionary)

    def get_stable_matching(self) -> dict | None:
        """
        Get the stable matching for the Student Project Allocation Problem With Ties algorithm.

        :return: dict, the stable matching for this instance
        """
        self.spas_alg.run()
        if self.spas_alg.is_stable:
            return self.spas_alg.stable_matching
        return None
