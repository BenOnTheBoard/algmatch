from random import randint, shuffle

from tests.abstractTestClasses.genericGeneratorInterface import (
    GenericGeneratorInterface,
)


class SRInstanceGenerator(GenericGeneratorInterface):
    def __init__(self, no_roommates, lower_bound, upper_bound):
        self.no_roommates = no_roommates
        self.li = lower_bound
        self.lj = upper_bound
        self._assert_valid_parameters()

        self.instance = dict()

        # lists of numbers that will be shuffled to get preferences
        self.available_roommates = [i + 1 for i in range(self.no_roommates)]

    def _assert_valid_parameters(self):
        assert self.no_roommates > 0 and isinstance(self.no_roommates, int), (
            "Number of roommates must be a postive integer."
        )
        assert isinstance(self.li, int) and isinstance(self.lj, int), (
            "Bounds must be integers."
        )
        assert self.li >= 0, "Lower bound is negative."
        assert self.lj < self.no_roommates, (
            "Upper bound is greater than the number of other roommates."
        )
        assert self.li <= self.lj, "Lower bound is greater than upper bound"

    def _reset_instance(self):
        self.instance = {i + 1: [] for i in range(self.no_roommates)}

    def generate_instance(self):
        self._reset_instance()
        self._generate_lists()
        return self.instance

    def _generate_lists(self):
        for r, r_list in self.instance.items():
            length = randint(self.li, self.lj)
            shuffle(self.available_roommates)

            possible_roommates = self.available_roommates.copy()
            possible_roommates.remove(r)

            r_list.extend(possible_roommates[:length])
