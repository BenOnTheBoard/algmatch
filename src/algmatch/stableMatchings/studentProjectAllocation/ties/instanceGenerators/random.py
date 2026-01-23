"""
Program to generate an instance of SPA-ST - Random
Student Project Allocation with Student and Lecturer preferences over projects
"""

import random
import math

from .abstract import AbstractInstanceGenerator


class SPASTIG_Random(AbstractInstanceGenerator):
    def __init__(
            self,
            student_tie_density,
            lecturer_tie_density,
            **kwargs
    ):
        super().__init__(**kwargs)

        self.student_tie_density = student_tie_density
        self.lecturer_tie_density = lecturer_tie_density

    def _generate_students(self):
        for student in self._sp:
            length = random.randint(self._li, self._lj) # randomly decide length of preference list
            project_list = list(self._plc.keys())
            for i in range(length):
                p = random.choice(project_list)
                project_list.remove(p) # avoid picking same project twice
                if i == 0 or random.uniform(0, 1) > self.student_tie_density:
                    self._sp[student].append([p])
                else:
                    self._sp[student][-1].append(p)
                self._plc[p][2].append(student)


    def _generate_lecturers(self):
        # number of projects lecturer can offer is between 1 and ceil(|projects| / |lecturers|)
        # done to ensure even distribution of projects amongst lecturers
        upper_bound = math.floor(self._num_projects / self._num_lecturers)
        project_list = list(self._plc.keys())

        for lecturer in self._lp:
            num_projects = random.randint(1, upper_bound)
            for _ in range(num_projects):
                p = random.choice(project_list)
                project_list.remove(p)
                self._assign_project_lecturer(p, lecturer)

        # while some projects are unassigned
        lecturer_list = list(self._lp.keys())
        while project_list:
            p = random.choice(project_list)
            project_list.remove(p)
            lecturer = random.choice(lecturer_list)
            self._assign_project_lecturer(p, lecturer)

        # decide ordered preference and capacity
        for lecturer in self._lp:
            pref = list(set(self._lp[lecturer][2][:]))
            if not pref: continue
            random.shuffle(pref)
            pref_with_ties = [[pref[0]]]

            for student in pref[1:]:
                if random.uniform(0, 1) <= self.lecturer_tie_density:
                    pref_with_ties[-1].append(student)
                else:
                    pref_with_ties.append([student])
            self._lp[lecturer][2] = pref_with_ties

            if self._force_lecturer_capacity:
                self._lp[lecturer][0] = self._force_lecturer_capacity
            else:
                self._lp[lecturer][0] = random.randint(self._lp[lecturer][3], self._lp[lecturer][4])
