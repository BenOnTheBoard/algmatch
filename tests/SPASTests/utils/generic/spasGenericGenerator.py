from tests.abstractTestClasses.genericGeneratorInterface import (
    GenericGeneratorInterface,
)


class SPASGenericGenerator(GenericGeneratorInterface):
    def __init__(self, students, projects, lecturers, lower_bound, upper_bound):
        self.no_students = students
        self.no_projects = projects
        self.no_lecturers = lecturers
        self.li = lower_bound
        self.lj = upper_bound
        self._assert_valid_parameters()

        self.instance = {"students": {}, "projects": {}, "lecturers": {}}

        # lists of numbers that will be shuffled to get preferences
        self.available_students = [i + 1 for i in range(self.no_students)]
        self.available_projects = [i + 1 for i in range(self.no_projects)]

    def _assert_valid_parameters(self):
        assert self.no_students > 0 and isinstance(self.no_students, int), (
            "Number of students must be a postive integer."
        )
        assert self.no_projects > 0 and isinstance(self.no_projects, int), (
            "Number of projects must be a postive integer."
        )
        assert self.no_lecturers > 0 and isinstance(self.no_lecturers, int), (
            "Number of projects must be a postive integer."
        )
        assert self.no_lecturers <= self.no_projects, (
            "There must be at least one project per lecturer."
        )

        assert isinstance(self.li, int) and isinstance(self.lj, int), (
            "Bounds must be integers."
        )
        assert self.li >= 0, "Lower bound is negative."
        assert self.lj <= self.no_projects, (
            "Upper bound is greater than the number of hospitals."
        )
        assert self.li <= self.lj, "Lower bound is greater than upper bound"

    def _reset_instance(self):
        self.instance = {
            "students": {i + 1: [] for i in range(self.no_students)},
            "projects": {
                i + 1: {"capacity": 0, "lecturer": None}
                for i in range(self.no_projects)
            },
            "lecturers": {
                i + 1: {"capacity": 0, "preferences": []}
                for i in range(self.no_lecturers)
            },
        }

    def generate_instance(self):
        self._reset_instance()
        self._generate_students()
        self._generate_projects()
        self._generate_lecturers()
        return self.instance

    def _generate_students(self):
        """
        Generates the students' preference lists for the instance.
        """
        raise NotImplementedError("Method not implemented by subclass.")

    def _generate_projects(self):
        """
        Generates the projects' capacities and lecturer-relations for the instance.
        """
        raise NotImplementedError("Method not implemented by subclass.")

    def _generate_lecturers(self):
        """
        Generates the lecturers' capacities and preferences for the instance.
        """
