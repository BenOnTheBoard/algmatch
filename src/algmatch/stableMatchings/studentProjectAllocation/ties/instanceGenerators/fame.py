"""
Program to generate an instance of SPA-P - Fame Euclidean
Student Project Allocation with Student and Lecturer preferences over projects
"""

import numpy as np

from algmatch.stableMatchings.studentProjectAllocation.SPA_P.instanceGenerators.euclidean import SPAPIG_Euclidean


class SPASTIG_FameEuclidean(SPAPIG_Euclidean):
    def __init__(
            self,
            num_dimensions: int = 5,
            max_fame: float = 0.4,
            **kwargs,
    ):
        super().__init__(num_dimensions=num_dimensions, **kwargs)
        self._max_fame = max_fame


    def _distance_function(self, points, point):
        return super()._distance_function(points, point) - self._project_fame


    def sample_all_points(self):
        super().sample_all_points()

        self._project_fame = np.random.uniform(0, self._max_fame, self._num_projects)
