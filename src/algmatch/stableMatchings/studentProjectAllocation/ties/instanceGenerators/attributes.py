"""
Program to generate an instance of SPA-ST - Attributes
Student Project Allocation with Student preferences over projects allowing ties
"""

import numpy as np

from algmatch.stableMatchings.studentProjectAllocation.ties.instanceGenerators.euclidean import SPASTIG_Euclidean


class SPASTIG_Attributes(SPASTIG_Euclidean):
    def __init__(
            self,
            num_dimensions: int = 5,
            **kwargs,
    ):
        super().__init__(num_dimensions=num_dimensions, **kwargs)


    def _distance_function(self, points, point):
        return np.dot(points, point)
