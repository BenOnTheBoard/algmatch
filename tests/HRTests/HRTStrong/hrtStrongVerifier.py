from algmatch.hospitalResidentsProblemWithTies import HospitalResidentsProblemWithTies

from tests.abstractTestClasses.abstractVerifier import AbstractVerifier
from tests.HRTests.utils.ties.hrtInstanceGenerator import HRTInstanceGenerator
from tests.HRTests.utils.ties.hrtEnumerator import HRTEnumerator


class HRTStrongVerifier(AbstractVerifier):
    def __init__(self, total_residents, total_hospitals, lower_bound, upper_bound):
        """
        It takes argument as follows (set in init):
            number of residents
            number of hospitals
            lower bound of the preference list length
            upper bound of the preference list length
        """

        self._total_residents = total_residents
        self._total_hospitals = total_hospitals
        self._lower_bound = lower_bound
        self._upper_bound = upper_bound

        generator_args = (total_residents, total_hospitals, lower_bound, upper_bound)

        AbstractVerifier.__init__(
            self,
            HospitalResidentsProblemWithTies,
            ("residents", "hospitals"),
            HRTInstanceGenerator,
            generator_args,
            HRTEnumerator,
            "strong",
        )
