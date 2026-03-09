from algmatch.stableMatchings.stableRoommatesProblem.srAbstract import SRAbstract


class SREnumerator(SRAbstract):
    def __init__(self, dictionary):
        SRAbstract.__init__(self, dictionary=dictionary)
        self.M = {r: {"assigned": None} for r in self.roommates}
        self.stable_matching_list = []

    def add_pair(self, r_a, r_b):
        self.M[r_a]["assigned"] = r_b
        self.M[r_b]["assigned"] = r_a

    def delete_pair(self, r_a, r_b):
        self.M[r_a]["assigned"] = None
        self.M[r_b]["assigned"] = None

    def save_matching(self):
        stable_matching = {}
        for roommate in self.roommates:
            if self.M[roommate]["assigned"] is None:
                stable_matching[roommate] = ""
            else:
                stable_matching[roommate] = self.M[roommate]["assigned"]
        self.stable_matching_list.append(stable_matching)

    def choose(self, i=1):
        # if every roommate is assigned
        if i > len(self.roommates):
            # if stable add to solutions list
            if self._check_stability():
                self.save_matching()

        else:
            r_a = f"r{i}"
            if self.M[r_a]["assigned"] is None:
                for r_b in self.roommates[r_a]["list"]:
                    if self.M[r_b]["assigned"] is None and int(r_a[1:]) < int(r_b[1:]):
                        self.add_pair(r_a, r_b)
                        self.choose(i + 1)
                        self.delete_pair(r_a, r_b)
            # case where the roommate is unassigned
            self.choose(i + 1)

    # alias with more readable name
    def find_stable_matchings(self) -> None:
        self.choose()
