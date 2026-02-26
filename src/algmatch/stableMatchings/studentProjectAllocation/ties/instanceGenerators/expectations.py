"""
Program to generate an instance of SPA-ST - Expectations Euclidean
Student Project Allocation with Student preferences over projects allowing ties
"""

import numpy as np

from algmatch.stableMatchings.studentProjectAllocation.ties.instanceGenerators.euclidean import SPASTIG_Euclidean


class SPASTIG_ExpectationsEuclidean(SPASTIG_Euclidean):
    def __init__(
            self,
            num_dimensions: int = 5,
            stdev: float = 0.5,
            **kwargs,
    ):
        super().__init__(num_dimensions=num_dimensions, **kwargs)
        self._stdev = stdev


    def __str__(self) -> str:
        return "SPASTIG_ExpectationsEuclidean"


    def sample_all_points(self):
        super().sample_all_points()

        self._project_points = np.random.normal(
            loc=self._project_points,
            scale=self._stdev,
        )
