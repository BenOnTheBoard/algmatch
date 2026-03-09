from algmatch.utils.generators.genericGeneratorInterface import (
    GenericGeneratorInterface,
)


class HRGenericGenerator(GenericGeneratorInterface):
    def __init__(self, residents, hospitals, lower_bound, upper_bound):
        self.no_residents = residents
        self.no_hospitals = hospitals
        self.li = lower_bound
        self.lj = upper_bound
        self._assert_valid_parameters()

        self.instance = {"residents": {}, "hospitals": {}}

        # lists of numbers that will be shuffled to get preferences
        self.available_residents = [i + 1 for i in range(self.no_residents)]
        self.available_hospitals = [i + 1 for i in range(self.no_hospitals)]

    def _assert_valid_parameters(self):
        assert self.no_residents > 0 and isinstance(self.no_residents, int), (
            "Number of residents must be a postive integer."
        )
        assert self.no_hospitals > 0 and isinstance(self.no_hospitals, int), (
            "Number of hospitals must be a postive integer."
        )
        assert isinstance(self.li, int) and isinstance(self.lj, int), (
            "Bounds must be integers."
        )
        assert self.li >= 0, "Lower bound is negative."
        assert self.lj <= self.no_hospitals, (
            "Upper bound is greater than the number of hospitals."
        )
        assert self.li <= self.lj, "Lower bound is greater than upper bound"

    def _reset_instance(self):
        self.instance = {
            "residents": {i + 1: [] for i in range(self.no_residents)},
            "hospitals": {
                i + 1: {"capacity": 0, "preferences": []}
                for i in range(self.no_hospitals)
            },
        }

    def generate_instance(self):
        self._reset_instance()
        self._generate_residents_lists()
        self._generate_hospitals_lists()
        return self.instance

    def _generate_residents_lists(self):
        """
        Generates the residents' preference lists for the instance.
        """
        raise NotImplementedError("Method not implemented by subclass.")

    def _generate_hospitals_lists(self):
        """
        Generates the hospitals' preference lists for the instance.
        """
        raise NotImplementedError("Method not implemented by subclass.")
