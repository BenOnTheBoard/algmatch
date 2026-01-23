"""
Program to generate an instance of SPA-P - Attributes
Student Project Allocation with Student and Lecturer preferences over projects
"""

import numpy as np

from algmatch.stableMatchings.studentProjectAllocation.SPA_P.instanceGenerators.euclidean import SPAPIG_Euclidean


class SPASTIG_Attributes(SPAPIG_Euclidean):
    def __init__(
            self,
            num_dimensions: int = 5,
            **kwargs,
    ):
        super().__init__(num_dimensions=num_dimensions, **kwargs)


    def _distance_function(self, points, point):
        return np.dot(points, point)
