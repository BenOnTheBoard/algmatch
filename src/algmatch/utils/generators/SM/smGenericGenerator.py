from algmatch.utils.generators.genericGeneratorInterface import (
    GenericGeneratorInterface,
)


class SMGenericGenerator(GenericGeneratorInterface):
    def __init__(self, men, women, lower_bound, upper_bound):
        self.no_men = men
        self.no_women = women
        self.li = lower_bound
        self.lj = upper_bound
        self._assert_valid_parameters()

        self.instance = {"men": {}, "women": {}}

        # lists of numbers that will be shuffled to get preferences
        self.available_men = [i + 1 for i in range(self.no_men)]
        self.available_women = [i + 1 for i in range(self.no_women)]

    def _assert_valid_parameters(self):
        assert self.no_men > 0 and isinstance(self.no_men, int), (
            "Number of men must be a postive integer."
        )
        assert self.no_women > 0 and isinstance(self.no_women, int), (
            "Number of women must be a postive integer."
        )
        assert isinstance(self.li, int) and isinstance(self.lj, int), (
            "Bounds must be integers."
        )
        assert self.li >= 0, "Lower bound is negative."
        assert self.lj <= min(self.no_men, self.no_women), (
            "Upper bound is greater than the number of men or the number of women."
        )
        assert self.li <= self.lj, "Lower bound is greater than upper bound"

    def _reset_instance(self):
        self.instance = {
            "men": {i + 1: [] for i in range(self.no_men)},
            "women": {i + 1: [] for i in range(self.no_women)},
        }

    def generate_instance(self):
        self._reset_instance()
        self._generate_men_lists()
        self._generate_women_lists()
        return self.instance

    def _generate_men_lists(self):
        """
        Generates the men's preference lists for the instance.
        """
        raise NotImplementedError("Method not implemented by subclass.")

    def _generate_women_lists(self):
        """
        Generates the women's preference lists for the instance.
        """
        raise NotImplementedError("Method not implemented by subclass.")
