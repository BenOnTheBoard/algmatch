"""
Class to provide interface for the Hospital/Residents Problem With Ties algorithms.
"""

import os

from algmatch.stableMatchings.hospitalResidentsProblem.ties.hrtStrongResidentOptimal import (
    HRTStrongResidentOptimal,
)
from algmatch.stableMatchings.hospitalResidentsProblem.ties.hrtStrongHospitalOptimal import (
    HRTStrongHospitalOptimal,
)
from algmatch.stableMatchings.hospitalResidentsProblem.ties.hrtSuperResidentOptimal import (
    HRTSuperResidentOptimal,
)
from algmatch.stableMatchings.hospitalResidentsProblem.ties.hrtSuperHospitalOptimal import (
    HRTSuperHospitalOptimal,
)

from algmatch.abstractClasses.stabilityType import StabilityType


class HospitalResidentsProblemWithTies:
    algorithms = {
        (StabilityType.SUPER, "residents"): HRTSuperResidentOptimal,
        (StabilityType.SUPER, "hospitals"): HRTSuperHospitalOptimal,
        (StabilityType.STRONG, "residents"): HRTStrongResidentOptimal,
        (StabilityType.STRONG, "hospitals"): HRTStrongHospitalOptimal,
    }

    def __init__(
        self,
        filename: str | None = None,
        dictionary: dict | None = None,
        optimised_side: str = "residents",
        stability_type: str = None,
    ) -> None:
        """
        Initialise the Hospital Residents Problem With Ties algorithms.

        :param filename: str, optional, default=None, the path to the file to read in the preferences from.
        :param dictionary: dict, optional, default=None, the dictionary of preferences.
        :param optimised_side: str, optional, default="residents", whether the algorithm is "residents" (default) or "hospitals" sided.
        :param stability_type_str: str, default=None, specifies the stability condition to be solved for.
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
        assert optimised_side in ("residents", "hospitals"), (
            "Optimised side must either be 'residents' or 'hospitals'"
        )

    def _validate_and_save_parameters(
        self, filename, dictionary, optimised_side, stability_type_str
    ):
        self._assert_valid_optimised_side(optimised_side)
        self.optimised_side = optimised_side.lower()
        self.stability_type = StabilityType.from_value(stability_type_str)
        self.filename = filename
        self.dictionary = dictionary

    def _set_algorithm(self):
        alg_key = (self.stability_type, self.optimised_side)
        if alg_key not in self.algorithms:
            raise NotImplementedError(
                "No algorithm has been implemented for this case."
            )
        alg_class = self.algorithms[alg_key]
        self.hr_alg = alg_class(filename=self.filename, dictionary=self.dictionary)

    def get_stable_matching(self) -> dict | None:
        """
        Get the stable matching for the Hospital/Residents Problem With Ties algorithm.

        :return: dict, the stable matching for this instance
        """
        self.hr_alg.run()
        if self.hr_alg.is_stable:
            return self.hr_alg.stable_matching
        return None
