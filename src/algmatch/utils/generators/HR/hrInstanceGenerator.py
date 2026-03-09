import random

from algmatch.utils.generators.HR.hrGenericGenerator import HRGenericGenerator


class HRInstanceGenerator(HRGenericGenerator):
    def __init__(self, residents, hospitals, lower_bound, upper_bound):
        super().__init__(residents, hospitals, lower_bound, upper_bound)

    def _generate_residents_lists(self):
        for res_list in self.instance["residents"].values():
            length = random.randint(self.li, self.lj)
            # we provide this many preferred hospitals at random
            random.shuffle(self.available_hospitals)
            res_list.extend(self.available_hospitals[:length])

    def _generate_hospitals_lists(self):
        for hos_dict in self.instance["hospitals"].values():
            hos_dict["capacity"] = random.randint(1, self.no_residents)
            # we provide a random ordering of all residents
            random.shuffle(self.available_residents)
            hos_dict["preferences"].extend(self.available_residents)
