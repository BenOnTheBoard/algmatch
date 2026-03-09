class SMGenericBruteForcer:
    def __init__(self):
        self.M = {m: {"assigned": None} for m in self.men} | {
            w: {"assigned": None} for w in self.women
        }
        self.stable_matching_list = []

    def add_pair(self, man, woman):
        self.M[man]["assigned"] = woman
        self.M[woman]["assigned"] = man

    def delete_pair(self, man, woman):
        self.M[man]["assigned"] = None
        self.M[woman]["assigned"] = None

    def save_matching(self):
        stable_matching = {"man_sided": {}, "woman_sided": {}}
        for man in self.men:
            if self.M[man]["assigned"] is None:
                stable_matching["man_sided"][man] = ""
            else:
                stable_matching["man_sided"][man] = self.M[man]["assigned"]
        for woman in self.women:
            if self.M[woman]["assigned"] is None:
                stable_matching["woman_sided"][woman] = ""
            else:
                stable_matching["woman_sided"][woman] = self.M[woman]["assigned"]
        self.stable_matching_list.append(stable_matching)

    def has_stability(self) -> bool:
        # Link to problem description
        raise NotImplementedError("Enumerators need to link to a stability definition.")

    def man_trial_order(self, man) -> str:
        # generator for an order of men in preference list
        raise NotImplementedError("Enumerators need to describe the order of matching.")

    def woman_trial_order(self, woman) -> str:
        # generator for an order of women in preference list
        raise NotImplementedError("Enumerators need to describe the order of matching.")
