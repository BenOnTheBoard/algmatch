import random

from algmatch.utils.generators.SM.smGenericGenerator import SMGenericGenerator


class SMGenerator(SMGenericGenerator):
    def __init__(self, men, women, lower_bound, upper_bound):
        SMGenericGenerator.__init__(self, men, women, lower_bound, upper_bound)

    def _generate_men_lists(self):
        for man_list in self.instance["men"].values():
            length = random.randint(self.li, self.lj)
            # we provide this many preferred women at random
            random.shuffle(self.available_women)
            man_list.extend(self.available_women[:length])

    def _generate_women_lists(self):
        for woman_list in self.instance["women"].values():
            length = random.randint(self.li, self.lj)
            #  we provide this many preferred men at random
            random.shuffle(self.available_men)
            woman_list.extend(self.available_men[:length])
