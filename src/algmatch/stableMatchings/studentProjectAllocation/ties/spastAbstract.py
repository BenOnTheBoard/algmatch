"""
Student Project Allocation With Lecturer Preferences Over Students
- With Ties
- Abstract class
"""

from copy import deepcopy
import os

from algmatch.stableMatchings.studentProjectAllocation.ties.spastPreferenceInstance import (
    SPASTPreferenceInstance,
)


class SPASTAbstract:
    def __init__(
        self,
        filename: str | None = None,
        dictionary: dict | None = None,
        stability_type: str = None,
    ) -> None:
        assert filename is not None or dictionary is not None, (
            "Either filename or dictionary must be provided"
        )
        assert not (filename is not None and dictionary is not None), (
            "Only one of filename or dictionary must be provided"
        )

        self._assert_valid_stability_type(stability_type)
        self.stability_type = stability_type.lower()

        if filename is not None:
            assert os.path.isfile(filename), f"File {filename} does not exist"
            self._reader = SPASTPreferenceInstance(filename=filename)

        if dictionary is not None:
            self._reader = SPASTPreferenceInstance(dictionary=dictionary)

        self.students = self._reader.students
        self.projects = self._reader.projects
        self.lecturers = self._reader.lecturers

        # we need original copies of the preference lists to check the stability of solutions
        self.original_students = deepcopy(self.students)
        self.original_lecturers = deepcopy(self.lecturers)

        self.M = {}  # provisional matching
        self.stable_matching = {
            "student_sided": {student: "" for student in self.students},
            "lecturer_sided": {lecturer: set() for lecturer in self.lecturers},
        }

        self.super_blocking_conditions = (
            self._blocking_pair_bi,
            self._blocking_pair_bii,
            self._blocking_pair_biii,
        )
        self.is_stable = False

    @staticmethod
    def _assert_valid_stability_type(st) -> None:
        assert st is not None, "Select a stability type - either 'super' or 'strong'"
        assert type(st) is str, "Stability type is not str'"
        assert st.lower() in ("super", "strong"), (
            "Stability type must be either 'super' or 'strong'"
        )

    def _get_lecturer_worst_existing_student(self, lecturer):
        existing_students = self.M[lecturer]["assigned"]

        if len(existing_students) == 0:
            return None

        def rank_comparator(x):
            return -self.lecturers[lecturer]["rank"][x]

        return min(existing_students, key=rank_comparator)

    def _get_project_worst_existing_student(self, project):
        existing_students = self.M[project]["assigned"]

        if len(existing_students) == 0:
            return None

        def rank_comparator(x):
            return -self.projects[project]["rank"][x]

        return min(existing_students, key=rank_comparator)

    def _blocking_pair_bi(self, _, project, lecturer):
        cj = self.projects[project]["capacity"]
        dk = self.original_lecturers[lecturer]["capacity"]

        project_occupancy = len(self.M[project]["assigned"])
        lecturer_occupancy = len(self.M[lecturer]["assigned"])

        if project_occupancy < cj and lecturer_occupancy < dk:
            return True
        return False

    def _blocking_pair_bii(self, student, project, lecturer):
        cj = self.projects[project]["capacity"]
        dk = self.original_lecturers[lecturer]["capacity"]

        project_occupancy = len(self.M[project]["assigned"])
        lecturer_occupancy = len(self.M[lecturer]["assigned"])

        if project_occupancy < cj and lecturer_occupancy == dk:
            Mlk_students = self.M[lecturer]["assigned"]
            if student in Mlk_students:  # s_i \in M(lk)
                return True

            lk_rankings = self.original_lecturers[lecturer]["rank"]
            student_rank = lk_rankings[student]
            worst_student = self._get_lecturer_worst_existing_student(lecturer)
            worst_student_rank = lk_rankings[worst_student]
            if student_rank <= worst_student_rank:
                return True
        return False

    def _blocking_pair_biii(self, student, project, _):
        cj = self.projects[project]["capacity"]
        project_occupancy = len(self.M[project]["assigned"])

        if project_occupancy == cj:
            lkj_rankings = self.projects[project]["rank"]
            student_rank = lkj_rankings[student]
            worst_student = self._get_project_worst_existing_student(project)
            worst_student_rank = lkj_rankings[worst_student]
            if student_rank <= worst_student_rank:
                return True
        return False

    def _check_super_stability(self) -> bool:
        # stability must be checked with regards to the original lists prior to deletions
        for student, s_prefs in self.original_students.items():
            matched_project = self.M[student]["assigned"]

            if matched_project is None:
                preferred_projects = s_prefs["list"]
            else:
                rank_matched_project = s_prefs["rank"][matched_project]
                # every project that s_i prefers to her matched project
                # or is indifferent between them
                preferred_projects = s_prefs["list"][: rank_matched_project + 1]

            for p_tie in preferred_projects:
                for project in p_tie:
                    if project == matched_project:
                        continue

                    lecturer = self.projects[project]["lecturer"]
                    for condition in self.super_blocking_conditions:
                        if condition(student, project, lecturer):
                            return False

        return True

    def _check_strong_stability(self) -> bool:
        raise NotImplementedError(
            "Strong stability algorithms have not yet been published for SPAST"
        )

    def _get_prefs(self, participant) -> dict:
        if participant in self.students:
            return self.students[participant]
        elif participant in self.projects:
            return self.projects[participant]
        elif participant in self.lecturers:
            return self.lecturers[participant]
        else:
            raise ValueError(f"{participant} is not a student, project, or lecturer.")

    def _get_pref_list(self, participant) -> list:
        return self._get_prefs(participant)["list"]

    def _get_pref_ranks(self, participant) -> dict:
        return self._get_prefs(participant)["rank"]

    def _get_pref_length(self, person) -> int:
        pref_list = self._get_pref_list(person)
        total = sum([len(tie) for tie in pref_list])
        return total

    def _get_head(self, person) -> set:
        pref_list = self._get_pref_list(person)
        idx = 0
        while idx < len(pref_list):
            head = pref_list[idx]
            if len(head) > 0:
                return head.copy()
            idx += 1
        return set()

    def _get_tail(self, person, return_idx=False) -> set:
        pref_list = self._get_pref_list(person)
        idx = len(pref_list) - 1
        while idx >= 0:
            tail = pref_list[idx]
            if len(tail) > 0:
                if return_idx:
                    return idx
                else:
                    return tail.copy()
            idx -= 1

        if return_idx:
            return -1
        raise ValueError("Pref_list empty")

    def _get_lecturer_occupancy(self, lecturer):
        return sum(
            len(self.M[p]["assigned"]) for p in self.lecturers[lecturer]["projects"]
        )

    def _assign(self, student, project, lecturer) -> None:
        self.M[student]["assigned"].add(project)
        self.M[project]["assigned"].add(student)
        self.M[lecturer]["assigned"].add(student)

    def _break_assignment(self, student, project, lecturer) -> None:
        self.M[student]["assigned"].discard(project)
        self.M[project]["assigned"].discard(student)

        student_still_assigned = any(
            [
                self.projects[p]["lecturer"] == lecturer
                for p in self.M[student]["assigned"]
            ]
        )
        if not student_still_assigned:
            self.M[lecturer]["assigned"].discard(student)

    def _delete_triple(self, student, project, lecturer) -> None:
        s_prefs = self._get_prefs(student)
        s_rank_p = s_prefs["rank"][project]
        s_prefs["list"][s_rank_p].remove(project)

        p_prefs = self._get_prefs(project)
        p_rank_s = p_prefs["rank"][student]
        p_prefs["list"][p_rank_s].remove(student)

        best_reject = self.projects[project]["best_reject"]
        if best_reject is None or p_rank_s < p_prefs["rank"][best_reject]:
            self.projects[project]["best_reject"] = student

        l_prefs = self._get_prefs(lecturer)
        l_prefs["times_ranked"][student] -= 1
        if l_prefs["times_ranked"][student] == 0:
            l_rank_s = l_prefs["rank"][student]
            l_prefs["list"][l_rank_s].remove(student)

    def _delete_tail_project(self, project) -> None:
        tail = self._get_tail(project)
        lecturer = self.projects[project]["lecturer"]
        for student in tail:
            self._break_assignment(student, project, lecturer)
            self._delete_triple(student, project, lecturer)

    def _delete_tail_lecturer(self, lecturer) -> None:
        tail = self._get_tail(lecturer)
        for student in tail:
            for project_tie in self._get_pref_list(student):
                for project in project_tie.copy():
                    if self.projects[project]["lecturer"] == lecturer:
                        self._break_assignment(student, project, lecturer)
                        self._delete_triple(student, project, lecturer)

    def _reject_project_lower_ranks(self, worst, project, lecturer) -> None:
        p_prefs = self._get_prefs(project)
        rank_worst = p_prefs["rank"][worst]
        for reject_tie in p_prefs["list"][rank_worst + 1 :]:
            for reject in reject_tie.copy():
                self._break_assignment(reject, project, lecturer)
                self._delete_triple(reject, project, lecturer)

    def _reject_lecturer_lower_ranks(self, worst, lecturer) -> None:
        l_prefs = self._get_prefs(lecturer)
        rank_worst = l_prefs["rank"][worst]
        for reject_tie in l_prefs["list"][rank_worst + 1 :]:
            for student in reject_tie.copy():
                for project_tie in self._get_pref_list(student):
                    for project in project_tie.copy():
                        if self.projects[project]["lecturer"] == lecturer:
                            self._break_assignment(student, project, lecturer)
                            self._delete_triple(student, project, lecturer)

    def _while_loop(self) -> bool:
        raise NotImplementedError("Method _while_loop must be implemented in subclass")

    def _save_student_sided(self) -> None:
        for student in self.students:
            project = self.M[student]["assigned"]
            if project is None:
                self.stable_matching["student_sided"][student] = ""
            else:
                self.stable_matching["student_sided"][student] = project

    def _save_lecturer_sided(self) -> None:
        for lecturer in self.lecturers:
            student_set = self.M[lecturer]["assigned"]
            self.stable_matching["lecturer_sided"][lecturer] = student_set

    def run(self) -> None:
        if self._while_loop():
            self._save_student_sided()
            self._save_lecturer_sided()

            if self.stability_type == "super":
                self.is_stable = self._check_super_stability()
            else:
                self.is_stable = self._check_strong_stability()

            if self.is_stable:
                return f"super-stable matching: {self.stable_matching}"
        return "no super-stable matching"
