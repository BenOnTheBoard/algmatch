import random

from algmatch.utils.generators.abstractTieGenerator import AbstractTieGenerator
from algmatch.utils.generators.HR.hrGenericGenerator import HRGenericGenerator


class HRTInstanceGenerator(HRGenericGenerator, AbstractTieGenerator):
    def __init__(self, residents, hospitals, lower_bound, upper_bound):
        HRGenericGenerator.__init__(
            self, residents, hospitals, lower_bound, upper_bound
        )
        AbstractTieGenerator.__init__(self)

    def _generate_residents_lists(self):
        for res_list in self.instance["residents"].values():
            random.shuffle(self.available_hospitals)
            length = random.randint(self.li, self.lj)

            self._generate_tied_list(
                res_list,
                self.available_hospitals[:length],
            )

    def _generate_hospitals_lists(self):
        for hos_dict in self.instance["hospitals"].values():
            # we provide a random ordering of all residents
            random.shuffle(self.available_residents)

            hos_dict["capacity"] = random.randint(1, self.no_residents)

            hos_list = hos_dict["preferences"]
            self._generate_tied_list(
                hos_list,
                self.available_residents,
            )
