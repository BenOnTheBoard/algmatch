"""
Program to generate an instance of SPA-P - Fame Euclidean Extended
Student Project Allocation with Student and Lecturer preferences over projects
"""

import numpy as np

from algmatch.stableMatchings.studentProjectAllocation.SPA_P.instanceGenerators.euclidean import SPAPIG_Euclidean


class SPASTIG_FameEuclideanExtended(SPAPIG_Euclidean):
    def __init__(
            self,
            num_dimensions: int = 5,
            max_fame_student: float = 0.4,
            max_fame_lecturer: float = 0.4,
            **kwargs,
    ):
        super().__init__(num_dimensions=num_dimensions, **kwargs)
        self._max_fame_student = max_fame_student
        self._max_fame_lecturer = max_fame_lecturer


    def _distance_function(self, points, point):
        return super()._distance_function(points, point) - self._fame

    
    def _generate_students(self):
        self._fame = self._project_fame_student
        super()._generate_students()


    def _generate_lecturers(self):
        self._fame = self._project_fame_lecturer
        super()._generate_lecturers()


    def sample_all_points(self):
        super().sample_all_points()

        self._project_fame_student = np.random.uniform(0, self._max_fame_student, self._num_projects)
        self._project_fame_lecturer = np.random.uniform(0, self._max_fame_lecturer, self._num_projects)
