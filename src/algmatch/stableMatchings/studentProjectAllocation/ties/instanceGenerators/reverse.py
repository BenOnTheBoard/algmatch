"""
Program to generate an instance of SPA-P - Reverse Euclidean
Student Project Allocation with Student and Lecturer preferences over projects
"""

from algmatch.stableMatchings.studentProjectAllocation.SPA_P.instanceGenerators.euclidean import SPAPIG_Euclidean


class SPASTIG_ReverseEuclidean(SPAPIG_Euclidean):
    def __init__(
            self,
            num_dimensions: int = 5,
            prop_s: float = 0.5,
            prop_l: float = 0.5,
            **kwargs,
    ):
        assert 0 <= prop_s <= 1, "Proportion of students must be between 0 and 1."
        assert 0 <= prop_l <= 1, "Proportion of lecturers must be between 0 and 1."

        super().__init__(num_dimensions=num_dimensions, **kwargs)
        self._prop_s = prop_s
        self._prop_l = prop_l


    def _get_ordered_list(self, points_list, idx, length=None):
        reverse = idx < (len(points_list) * self._prop) // 1
        return super()._get_ordered_list(
            points_list,
            idx,
            length=length,
            reverse=reverse,
        )


    def _generate_students(self):
        self._prop = self._prop_s
        super()._generate_students()


    def _generate_lecturers(self):
        self._prop = self._prop_l
        super()._generate_lecturers()
