from algmatch.utils.enumerators.SM.smGenericBruteForcer import SMGenericBruteForcer


class SMGenericEnumerator(SMGenericBruteForcer):
    def __init__(self):
        SMGenericBruteForcer.__init__(self)

    def choose(self, i=1):
        # if every man is assigned
        if i > len(self.men):
            # if stable add to solutions list
            if self.has_stability():
                self.save_matching()

        else:
            man = "m" + str(i)
            for woman in self.man_trial_order(man):
                # avoid the multiple assignment of women
                if self.M[woman]["assigned"] is None:
                    self.add_pair(man, woman)
                    self.choose(i + 1)
                    self.delete_pair(man, woman)
            # case where the man is unassigned
            self.choose(i + 1)

    # alias with more readable name
    def find_stable_matchings(self) -> None:
        self.choose()
