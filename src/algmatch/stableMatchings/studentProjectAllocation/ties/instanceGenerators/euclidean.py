"""
Program to generate an instance of SPA-ST - Euclidean
Student Project Allocation with Student preferences over projects allowing ties
"""

import numpy as np
import random

from algmatch.stableMatchings.studentProjectAllocation.ties.instanceGenerators.abstract import AbstractInstanceGenerator


class SPASTIG_Euclidean(AbstractInstanceGenerator):
    def __init__(
            self,
            num_dimensions: int = 5,
            **kwargs,
    ):
        assert num_dimensions > 0, "Number of dimensions must be greater than 0."

        super().__init__(**kwargs)
        self._num_dimensions = num_dimensions
        self.to_project_string = lambda x: f'p{x+1}'


    def _sample_points(self, num_points: int):
        return np.random.uniform(0, 1, (num_points, self._num_dimensions))


    def _distance_function(self, points, point):
        return np.linalg.norm(points - point, axis=1)


    def _get_ordered_list(
            self,
            points_list,
            other_list,
            idx,
            prefix,
            length=None,
            reverse=False
    ):
        return list(map(
            lambda x: f'{prefix}{x+1}',
            np.argsort(
                self._distance_function(other_list, points_list[idx])
            )[::-1 if reverse else 1][:length]
        ))


    def _generate_students(self):
        for i, student in enumerate(self._sp):
            pref_list = self._get_ordered_list(
                self._student_points,
                self._project_points,
                i,
                'p',
                random.randint(self._li, self._lj)
            )
            for p in pref_list:
                self._plc[p][2].append(student)
            self._sp[student] = self._add_ties_to_list(pref_list, self.student_tie_density)


    def _generate_lecturers(self):
        # number of projects lecturer can offer is between 1 and ceil(|projects| / |lecturers|)
        # done to ensure even distribution of projects amongst lecturers
        upper_bound_lecturers = self._num_projects // self._num_lecturers
        project_list = list(self._plc.keys())

        for lecturer in self._lp:
            num_projects = random.randint(1, upper_bound_lecturers)
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
        for i, lecturer in enumerate(self._lp):
            ordered_student_list = self._get_ordered_list(
                self._lecturer_points,
                self._student_points,
                i,
                's'
            )
            self._lp[lecturer][2] = self._add_ties_to_list(
                [s for s in ordered_student_list if s in self._lp[lecturer][2]],
                self.lecturer_tie_density
            )

            if self._force_lecturer_capacity:
                self._lp[lecturer][0] = self._force_lecturer_capacity
            else:
                self._lp[lecturer][0] = random.randint(self._lp[lecturer][3], self._lp[lecturer][4])


    def sample_all_points(self):
        self._student_points = self._sample_points(self._num_students)
        self._project_points = self._sample_points(self._num_projects)
        self._lecturer_points = self._sample_points(self._num_lecturers)


    def generate_instance(self):
        self.sample_all_points()
        super().generate_instance()
