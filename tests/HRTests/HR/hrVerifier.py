from algmatch.hospitalResidentsProblem import HospitalResidentsProblem

from tests.abstractTestClasses.abstractVerifier import AbstractVerifier
from algmatch.utils.generators.HR.hrInstanceGenerator import HRInstanceGenerator
from tests.HRTests.utils.hrEnumerator import HREnumerator


class HRVerifier(AbstractVerifier):
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
            HospitalResidentsProblem,
            ("residents", "hospitals"),
            HRInstanceGenerator,
            generator_args,
            HREnumerator,
        )
