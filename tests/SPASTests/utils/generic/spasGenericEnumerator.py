from tests.SPASTests.utils.generic.spasGenericBruteForcer import SPASGenericBruteForcer


class SPASGenericEnumerator(SPASGenericBruteForcer):
    def __init__(self):
        super().__init__()

    def add_triple(self, student, project, lecturer):
        super().add_triple(student, project, lecturer)
        if self.project_is_full(project):
            self.full_projects.add(project)
        if self.lecturer_is_full(lecturer):
            self.full_lecturers.add(lecturer)

    def delete_triple(self, student, project, lecturer):
        super().delete_triple(student, project, lecturer)
        self.full_projects.discard(project)
        self.full_lecturers.discard(lecturer)

    def choose(self, i=1) -> None:
        # if every student is assigned
        if i > len(self.students):
            if self.has_stability():
                self.save_matching()

        else:
            student = f"s{i}"
            for project in self.student_trial_order(student):
                if project not in self.full_projects:
                    lecturer = self.projects[project]["lecturer"]
                    if lecturer not in self.full_lecturers:
                        self.add_triple(student, project, lecturer)

                        self.choose(i + 1)

                        self.delete_triple(student, project, lecturer)
            # case where the student is unassigned
            self.choose(i + 1)

    # alias with more readable name
    def find_stable_matchings(self) -> None:
        self.choose()
