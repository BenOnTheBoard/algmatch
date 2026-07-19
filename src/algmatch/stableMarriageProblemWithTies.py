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

from algmatch.abstractClasses.stabilityType import StabilityType


class StableMarriageProblemWithTies:
    algorithms = {
        (StabilityType.SUPER, "men"): SMTSuperManOriented,
        (StabilityType.SUPER, "women"): SMTSuperWomanOriented,
        (StabilityType.STRONG, "men"): SMTStrongManOptimal,
        (StabilityType.STRONG, "women"): SMTStrongWomanOptimal,
    }

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
        optimised_side = optimised_side.lower()
        assert optimised_side in ("men", "women"), (
            "Optimised side must either be 'men' or 'women'"
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
        self.sm_alg = alg_class(filename=self.filename, dictionary=self.dictionary)

    def get_stable_matching(self) -> dict | None:
        """
        Get the stable matching for the Stable Marriage Problem With Ties algorithm.

        :return: dict, the stable matching for this instance
        """
        self.sm_alg.run()
        if self.sm_alg.is_stable:
            return self.sm_alg.stable_matching
        return None
