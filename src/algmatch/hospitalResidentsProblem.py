"""
Class to provide interface for the Hospital/Residents Problem algorithm.
"""

from algmatch.stableMatchings.hospitalResidentsProblem.noTies.hrResidentOptimal import (
    HRResidentOptimal,
)
from algmatch.stableMatchings.hospitalResidentsProblem.noTies.hrHospitalOptimal import (
    HRHospitalOptimal,
)
from algmatch.abstractClasses.preferenceSource import PreferenceSource


class HospitalResidentsProblem:
    def __init__(
        self,
        filename: str | None = None,
        dictionary: dict | None = None,
        optimised_side: str = "residents",
    ) -> None:
        """
        Initialise the Hospital Residents Problem algorithms.

        :param filename: str, optional, default=None, the path to the file to read in the preferences from.
        :param dictionary: dict, optional, default=None, the dictionary of preferences.
        :param optimised_side: str, optional, default="resident", whether the algorithm is "resident" (default) or "hospital" sided.
        """
        self.source = PreferenceSource(filename=filename, dictionary=dictionary)

        assert type(optimised_side) is str, "Param optimised_side must be of type str"
        optimised_side = optimised_side.lower()
        assert optimised_side in ("residents", "hospitals"), (
            "Optimised side must either be 'residents' or 'hospitals'"
        )

        if optimised_side == "residents":
            self.hr_alg = HRResidentOptimal(source=self.source)
        else:
            self.hr_alg = HRHospitalOptimal(source=self.source)

    def get_stable_matching(self) -> dict | None:
        """
        Get the stable matching for the Hospital/Residents Problem algorithm.

        :return: dict, the stable matching for this instance
        """
        self.hr_alg.run()
        if self.hr_alg.is_stable:
            return self.hr_alg.stable_matching
        return None
