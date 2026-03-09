import random


class AbstractTieGenerator:
    def __init__(self):
        self.tie_density = 0.5  # default to mixed

    def set_tie_density(self, tie_density):
        assert tie_density >= 0 and tie_density <= 1, "Tie density must be in [0,1]."
        self.tie_density = tie_density

    def _generate_tied_list(self, target, contents):
        if contents:
            target.append([contents[0]])

        for entity in contents[1:]:
            if random.uniform(0, 1) < self.tie_density:
                target[-1].append(entity)
            else:
                target.append([entity])
