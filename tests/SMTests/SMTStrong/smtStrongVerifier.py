from algmatch.stableMarriageProblemWithTies import StableMarriageProblemWithTies

from tests.abstractTestClasses.abstractVerifier import AbstractVerifier
from tests.SMTests.utils.ties.smtInstanceGenerator import SMTInstanceGenerator
from tests.SMTests.utils.ties.smtEnumerator import SMTEnumerator


class SMTStrongVerifier(AbstractVerifier):
    def __init__(self, total_men, total_women, lower_bound, upper_bound):
        """
        It takes argument as follows (set in init):
            number of men
            number of women
            lower bound of the preference list length
            upper bound of the preference list length
        """

        self._total_men = total_men
        self._total_women = total_women
        self._lower_bound = lower_bound
        self._upper_bound = upper_bound

        generator_args = (total_men, total_women, lower_bound, upper_bound)

        AbstractVerifier.__init__(
            self,
            StableMarriageProblemWithTies,
            ("men", "women"),
            SMTInstanceGenerator,
            generator_args,
            SMTEnumerator,
            "strong",
        )
