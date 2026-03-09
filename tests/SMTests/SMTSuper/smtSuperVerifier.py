from algmatch import SMT
from algmatch.utils import SMTEnumerator, SMTGenerator

from tests.abstractTestClasses.abstractVerifier import AbstractVerifier


class SMTSuperVerifier(AbstractVerifier):
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
            SMT,
            ("men", "women"),
            SMTGenerator,
            generator_args,
            SMTEnumerator,
            "super",
        )
