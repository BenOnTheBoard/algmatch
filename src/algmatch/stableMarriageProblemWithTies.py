"""
Class to provide interface for the Stable Marriage Problem With Ties algorithms.
"""

import os
from algmatch.stableMatchings.stableMarriageProblem.ties.smtSuperManOriented import (
    SMTSuperManOriented,
)
from algmatch.stableMatchings.stableMarriageProblem.ties.smtSuperWomanOriented import (
    SMTSuperWomanOriented,
)
from algmatch.stableMatchings.stableMarriageProblem.ties.smtStrongManOptimal import (
    SMTStrongManOptimal,
)
from algmatch.stableMatchings.stableMarriageProblem.ties.smtStrongWomanOptimal import (
    SMTStrongWomanOptimal,
)
from algmatch.stableMatchings.stableMarriageProblem.ties.smtAbstract import SMTAbstract


class StableMarriageProblemWithTies:
    def __init__(
        self,
        filename: str | None = None,
        dictionary: dict | None = None,
        optimised_side: str = "men",
        stability_type: str = None,
    ) -> None:
        """
        Initialise the Stable Marriage Problem With Ties algorithm.

        :param filename: str, optional, default=None, the path to the file to read in the preferences from.
        :param dictionary: dict, optional, default=None, the dictionary of preferences.
        :param optimised_side: str, optional, default="men", whether the algorithm is "men" (default) or "women" sided.
        :param stability_type: str, optional, default=None which kind of matching to look for. Must be either "strong" or "super".
        """
        if filename is not None:
            filename = os.path.join(os.getcwd(), filename)

        self._validate_and_save_parameters(
            filename, dictionary, optimised_side, stability_type
        )
        self._set_algorithm()

    def _assert_valid_optimised_side(self, optimised_side):
        assert type(optimised_side) is str, "Param optimised_side must be of type str"
        assert optimised_side in ("men", "women"), (
            "Optimised side must either be 'men' or 'women'"
        )

    def _validate_and_save_parameters(
        self, filename, dictionary, optimised_side, stability_type
    ):
        self._assert_valid_optimised_side(optimised_side)
        self.optimised_side = optimised_side.lower()

        SMTAbstract._assert_valid_stability_type(stability_type)
        self.stability_type = stability_type.lower()

        self.filename = filename
        self.dictionary = dictionary

    def _set_algorithm(self):
        if self.stability_type == "super":
            if self.optimised_side == "men":
                self.sm_alg = SMTSuperManOriented(
                    filename=self.filename, dictionary=self.dictionary
                )
            else:
                self.sm_alg = SMTSuperWomanOriented(
                    filename=self.filename, dictionary=self.dictionary
                )
        elif self.stability_type == "strong":
            if self.optimised_side == "men":
                self.sm_alg = SMTStrongManOptimal(
                    filename=self.filename, dictionary=self.dictionary
                )
            else:
                self.sm_alg = SMTStrongWomanOptimal(
                    filename=self.filename, dictionary=self.dictionary
                )
        else:
            raise ValueError('stability_type must be either "strong" or "super".')

    def get_stable_matching(self) -> dict | None:
        """
        Get the stable matching for the Stable Marriage Problem With Ties algorithm.

        :return: dict, the stable matching for this instance
        """
        self.sm_alg.run()
        if self.sm_alg.is_stable:
            return self.sm_alg.stable_matching
        return None
