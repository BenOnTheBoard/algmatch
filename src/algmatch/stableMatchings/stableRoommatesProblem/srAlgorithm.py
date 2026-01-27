"""
Algorithm to produce a stable matching.
"""

from algmatch.stableMatchings.stableRoommatesProblem.srAbstract import SRAbstract


class SRAlgorithm(SRAbstract):
    def __init__(
        self, filename: str | None = None, dictionary: dict | None = None
    ) -> None:
        super().__init__(filename=filename, dictionary=dictionary)

        self.unassigned_roommates = set()

        for roommate, r_prefs in self.roommates.items():
            if len(r_prefs["list"]) > 0:
                self.unassigned_roommates.add(roommate)
            self.M[roommate] = {"assigned": None}

    def _delete_pair(self, r_a, r_b):
        self.roommates[r_a]["list"].remove(r_b)
        self.roommates[r_b]["list"].remove(r_a)

        if len(self.roommates[r_a]["list"]) == 0:
            self.unassigned_roommates.discard(r_a)
        if len(self.roommates[r_b]["list"]) == 0:
            self.unassigned_roommates.discard(r_b)

    def _engage(self, r_a, r_b):
        self.M[r_b]["assigned"] = r_a

    def _free_up(self, r):
        if len(self.roommates[r]["list"]) > 0:
            self.unassigned_roommates.add(r)

    def proposal_phase(self):
        """
        Stable marriage-like proposal and refusal sequence
        """
        while self.unassigned_roommates:
            r_a = self.unassigned_roommates.pop()
            r_b = self.roommates[r_a]["list"][0]
            r_b_partner = self.M[r_b]["assigned"]

            if r_b_partner is not None:
                self._free_up(r_b_partner)
            self._engage(r_a, r_b)

            # using ranks might also be ok here
            rank_r_a = self.roommates[r_b]["list"].index(r_a)
            for reject in self.roommates[r_b]["list"][rank_r_a + 1 :]:
                self._delete_pair(reject, r_b)

    def locate_cycle(self, p_1):
        """
        Given a roommate p_1 who's reduced preference list contains more than one
        element, we identify a cycle of roommates, p_1,...,p_n. We want the roommate
        who holds their proposals to reject them. p_{i+1} is being held by q_i. We
        return only these q_i that need to make a rejection.
        """
        p = []
        q = []
        cur_p = p_1
        while cur_p not in p:
            p.append(cur_p)
            cur_q = self.roommates[cur_p]["list"][1]
            q.append(cur_q)
            cur_p = self.roommates[cur_q]["list"][-1]
        cycle_start = p.index(cur_p)

        if cycle_start == 0:
            return [q[-1]] + q[:-1]
        else:
            return q[cycle_start - 1 : -1]

    def cycle_phase(self):
        for candidate in self.roommates:
            length = len(self.roommates[candidate]["list"])
            if length != 1:
                r_a = candidate
                break

        rejecters = self.locate_cycle(r_a)
        for r_b in rejecters:
            partner = self.M[r_b]["assigned"]
            self._free_up(partner)
            self.M[r_b]["assigned"] = None
            self._delete_pair(r_b, partner)

    def halting_condition(self):
        if any(len(self.roommates[r]["list"]) == 0 for r in self.roommates):
            return False
        elif all(len(self.roommates[r]["list"]) == 1 for r in self.roommates):
            return False
        else:
            return True

    def _while_loop(self):
        self.proposal_phase()
        while self.halting_condition():
            self.cycle_phase()
            self.proposal_phase()
