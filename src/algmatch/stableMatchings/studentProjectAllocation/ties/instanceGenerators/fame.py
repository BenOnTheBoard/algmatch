"""
Program to generate an instance of SPA-ST - Fame Euclidean
Student Project Allocation with Student preferences over projects allowing ties
"""

import numpy as np

from algmatch.stableMatchings.studentProjectAllocation.ties.instanceGenerators.euclidean import SPASTIG_Euclidean


class SPASTIG_FameEuclidean(SPASTIG_Euclidean):
    def __init__(
            self,
            num_dimensions: int = 5,
            max_fame: float = 0.4,
            **kwargs,
    ):
        super().__init__(num_dimensions=num_dimensions, **kwargs)
        self._max_fame = max_fame


    def __str__(self) -> str:
        return "SPASTIG_FameEuclidean"


    def _distance_function(self, points, point):
        return super()._distance_function(points, point) - self._fame_values


    def _generate_students(self):
        self._fame_values = np.random.uniform(0, self._max_fame, self._num_projects)
        super()._generate_students()


    def _generate_lecturers(self):
        self._fame_values = np.random.uniform(0, self._max_fame, self._num_students)
        super()._generate_lecturers()
