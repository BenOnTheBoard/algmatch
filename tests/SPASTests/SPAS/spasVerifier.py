from algmatch.studentProjectAllocation import StudentProjectAllocation

from tests.abstractTestClasses.abstractVerifier import AbstractVerifier
from algmatch.utils.generators.SPAS.spasGenerator import SPASGenerator
from algmatch.utils.enumerators.SPAS.spasEnumerator import SPASEnumerator


class SPASVerifier(AbstractVerifier):
    def __init__(
        self, total_students, total_projects, total_lecturers, lower_bound, upper_bound
    ):
        """
        It takes argument as follows (set in init):
            number of students
            number of projects
            number of lecturers
            lower bound of the students' preference list length
            upper bound of the students' preference list length
        """

        self._total_students = total_students
        self._total_projects = total_projects
        self._total_lecturers = total_lecturers
        self._lower_bound = lower_bound
        self._upper_bound = upper_bound

        generator_args = (
            total_students,
            total_projects,
            total_lecturers,
            lower_bound,
            upper_bound,
        )

        AbstractVerifier.__init__(
            self,
            StudentProjectAllocation,
            ("students", "lecturers"),
            SPASGenerator,
            generator_args,
            SPASEnumerator,
        )
