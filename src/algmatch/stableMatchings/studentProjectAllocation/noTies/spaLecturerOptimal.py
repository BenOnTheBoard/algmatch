"""
Student Project Allocation - Lecturer Optimal version
"""

from algmatch.stableMatchings.studentProjectAllocation.noTies.spaAbstract import SPAAbstract


class SPALecturerOptimal(SPAAbstract):
    def __init__(
        self, filename: str | None = None, dictionary: dict | None = None
    ) -> None:
        super().__init__(filename=filename, dictionary=dictionary)

        self.under_subscribed_lecturers = list(self.lecturers.keys())

        for student in self.students:
            self.M[student] = {"assigned": None}

        for project in self.projects:
            self.M[project] = {"assigned": set()}

        for lecturer in self.lecturers:
            self.M[lecturer] = {"assigned": set()}

    def _delete(self, student, project):
        self.students[student]["list"].remove(project)
        self.projects[project]["list"].remove(student)

    def _check_pair_conditions(self, s_i, p_j, L_k):
        # s_i is not provisionally assigned to p_j
        # and p_j in P_k is under subscribed
        # and s_i in L_k^j

        return (
            self.M[s_i]["assigned"] != p_j
            and p_j in self.lecturers[L_k]["projects"]
            and len(self.M[p_j]["assigned"]) < self.projects[p_j]["capacity"]
        )

    def _find_valid_pair(self, L_k):
        # s_i is first valid on L_k list
        # p_j is first valid on s_i list

        for s_i in self.lecturers[L_k]["list"]:
            for p_j in self.students[s_i]["list"]:
                if self._check_pair_conditions(s_i, p_j, L_k):
                    return (s_i, p_j)

    def _break_assignment(self, student):
        p = self.M[student]["assigned"]
        L = self.projects[p]["lecturer"]
        self.M[student]["assigned"] = None
        self.M[p]["assigned"].remove(student)

        # add under-subscribed lecturer to under_subscribed_lecturers
        if len(self.M[p]["assigned"]) == self.projects[p]["lower_quota"]:
            self.under_subscribed_lecturers.insert(int(L[1:]) - 1, L)

        self.M[L]["assigned"].remove(student)

    def _provisionally_assign(self, student, project, lecturer):
        self.M[student]["assigned"] = project
        self.M[project]["assigned"].add(student)
        self.M[lecturer]["assigned"].add(student)

    def _while_loop(self):
        while len(self.under_subscribed_lecturers) > 0:
            L_k = self.under_subscribed_lecturers[0]
            pair = self._find_valid_pair(L_k)

            if pair is not None:
                s_i, p_j = pair
            else:
                # cannot find a valid pair, continue to next lecturer
                self.under_subscribed_lecturers.remove(L_k)
                continue

            # if s_i is provisionally assigned to some project p, break assignment
            if self.M[s_i]["assigned"] is not None:
                self._break_assignment(s_i)

            # provisionally assign s_i to p_j and to L_k
            self._provisionally_assign(s_i, p_j, L_k)

            # for each successor p of p_j on s_i's list, delete (s_i, p)
            p_j_pos = self.students[s_i]["list"].index(p_j)
            for p in self.students[s_i]["list"][p_j_pos + 1 :]:
                self._delete(s_i, p)

            # check if lecturer is still under subscribed
            # TODO: check is this necessary since we are re-building list anyway?
            if len(self.M[L_k]["assigned"]) == self.lecturers[L_k]["capacity"]:
                self.under_subscribed_lecturers.remove(L_k)

            # build under subscribed list
            self.under_subscribed_lecturers = []
            for L in self.lecturers:
                if len(self.M[L]["assigned"]) < self.lecturers[L]["capacity"]:
                    self.under_subscribed_lecturers.append(L)
