"""
Class to provide interface for the Stable Roommates Problem algorithm.
"""

import os

from algmatch.stableMatchings.stableRoommatesProblem.srAlgorithm import SRAlgorithm


class StableRoommatesProblem:
    def __init__(
        self,
        filename: str | None = None,
        dictionary: dict | None = None,
    ) -> None:
        """
        Initialise the Stable Roommates Problem algorithm.

        :param filename: str, optional, default=None, the path to the file to read in the preferences from.
        :param dictionary: dict, optional, default=None, the dictionary of preferences.
        """
        if filename is not None:
            filename = os.path.join(os.getcwd(), filename)

        self.sr_alg = SRAlgorithm(filename=filename, dictionary=dictionary)

    def get_stable_matching(self) -> dict | None:
        """
        Get the stable matching for the Stable Roommates Problem algorithm.

        :return: dict, the stable matching for this instance
        """
        self.sr_alg.run()
        if self.sr_alg.is_stable:
            return self.sr_alg.stable_matching
        return None
