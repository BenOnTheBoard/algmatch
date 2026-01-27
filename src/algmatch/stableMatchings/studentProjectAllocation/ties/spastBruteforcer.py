from algmatch.stableMatchings.studentProjectAllocation.ties.spastAbstract import SPASTAbstract


class SPASTBruteforcer(SPASTAbstract):
    def __init__(self, filename):
        super().__init__(filename=filename, stability_type="strong")

        self.M = {}
        self.setup_M()
        self.ssm_list = []

        # This lets us order students in the stable matching by number.
        # We cannot use 'sorted' without this key because that uses lexial order.
        self.student_order_comparator = lambda s: int(s[1:])

    def project_is_overfull(self, p):
        return self.projects[p]["upper_quota"] < len(self.M[p]["assigned"])

    def lecturer_is_overfull(self, L):
        return self.lecturers[L]["upper_quota"] < len(self.M[L]["assigned"])

    def add_triple(self, student, project, lecturer):
        self.M[student]["assigned"] = project
        self.M[project]["assigned"].add(student)
        self.M[lecturer]["assigned"].add(student)

    def delete_triple(self, student, project, lecturer):
        self.M[student]["assigned"] = None
        self.M[project]["assigned"].remove(student)
        self.M[lecturer]["assigned"].remove(student)

    def save_matching(self):
        stable_matching = {}
        for student in self.students:
            assigned_project = self.M[student]["assigned"]
            if assigned_project is None:
                stable_matching[student] = ""
            else:
                stable_matching[student] = assigned_project
        self.ssm_list.append(stable_matching)

    def setup_M(self):
        self.M.clear()
        self.M.update({s: {"assigned": None} for s in self.students})
        self.M.update({p: {"assigned": set()} for p in self.projects})
        self.M.update({L: {"assigned": set()} for L in self.lecturers})

    def choose(self, i=1):
        # if every student is assigned
        if i > len(self.students):
            for project in self.projects:
                if self.project_is_overfull(project):
                    return
            for lecturer in self.lecturers:
                if self.lecturer_is_overfull(lecturer):
                    return
            # if stable add to solutions list
            if self._check_strong_stability():
                self.save_matching()

        else:
            student = f"s{i}"
            for tie in self.students[student]["list"]:
                for project in tie:
                    lecturer = self.projects[project]["lecturer"]

                    self.add_triple(student, project, lecturer)
                    self.choose(i + 1)
                    self.delete_triple(student, project, lecturer)

            # case where the student is unassigned
            self.choose(i + 1)

    def get_ssm_list(self):
        return self.ssm_list
