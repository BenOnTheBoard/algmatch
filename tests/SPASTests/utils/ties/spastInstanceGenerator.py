from random import randint, shuffle

from tests.abstractTestClasses.abstractTieGenerator import AbstractTieGenerator
from tests.SPASTests.utils.generic.spasGenericGenerator import SPASGenericGenerator


class SPASTInstanceGenerator(SPASGenericGenerator, AbstractTieGenerator):
    def __init__(self, students, projects, lecturers, lower_bound, upper_bound):
        SPASGenericGenerator.__init__(
            self, students, projects, lecturers, lower_bound, upper_bound
        )
        AbstractTieGenerator.__init__(self)

    def _generate_students(self):
        for s_list in self.instance["students"].values():
            length = randint(self.li, self.lj)
            shuffle(self.available_projects)

            self._generate_tied_list(
                s_list,
                self.available_projects[:length],
            )

    def _generate_projects(self):
        projectless_lecturers = {i + 1 for i in range(self.no_lecturers)}
        for p_info in self.instance["projects"].values():
            p_info["capacity"] = randint(1, self.no_students)
            if projectless_lecturers:
                lecturer = projectless_lecturers.pop()
                p_info["lecturer"] = lecturer
            else:
                p_info["lecturer"] = randint(1, self.no_lecturers)

    def _generate_lecturers(self):
        l_capacity_bounds = {
            i + 1: {"max": 0, "total": 0} for i in range(self.no_lecturers)
        }

        for p_info in self.instance["projects"].values():
            l_bounds = l_capacity_bounds[p_info["lecturer"]]
            l_bounds["total"] += p_info["capacity"]
            if l_bounds["max"] < p_info["capacity"]:
                l_bounds["max"] = p_info["capacity"]

        for L, l_info in self.instance["lecturers"].items():
            l_bounds = l_capacity_bounds[L]
            l_info["capacity"] = randint(l_bounds["max"], l_bounds["total"])
            shuffle(self.available_students)

            self._generate_tied_list(
                l_info["preferences"],
                self.available_students,
            )
