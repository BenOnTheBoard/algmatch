"""
Abstract Instance Generator for SPA-ST
Student Project Allocation with Student preferences over projects allowing ties
"""

from abc import ABC, abstractmethod
import math
import random


class AbstractInstanceGenerator(ABC):
    def __init__(
            self,
            num_students,
            lower_bound,
            upper_bound,
            num_projects,
            num_lecturers,
            student_tie_density=0.5,
            lecturer_tie_density=0.5,
            force_project_capacity=0,
            force_lecturer_capacity=0
    ) -> None:
        """
        * the density of tie in the preference lists is a number between 0 and 1 (inclusive)
            - if the tie density is 0 on both sides, then the program writes an instance of SPA-S
            without ties
            - if the tie density is 1 on both sides, then the program writes an instance of SPA-ST,
            where each preference list is a single tie of length 1
        
        * the tie density given is the probability (decided at random) that a project (or student) will be tied
        with its successor.

        * a lower tie density value corresponds to fewer ties.

        :param num_students: int, number of students
        :param lower_bound: int, lower bound of the students' preference list length
        :param upper_bound: int, upper bound of the students' preference list length
        :param num_projects: int, number of projects
        :param num_lecturers: int, number of lecturers
        :param student_tie_density: float, [0, 1], the density of tie in the students preference list 
        :param lecturer_tie_density: float, [0, 1], the density of tie in the lecturers preference list
        :param force_project_capacity: int, value to force project capacity
        :param force_lecturer_capacity: int, value to force lecturer capacity
        """
        assert lower_bound <= upper_bound, "Lower bound must be less than or equal to upper bound."
        assert upper_bound <= num_projects, "Upper bound must be less than or equal to the number of projects."

        self._num_students: int = num_students
        self._num_projects: int = num_projects
        self._num_lecturers: int = num_lecturers

        self._force_project_capacity: int = force_project_capacity
        self._force_lecturer_capacity: int = force_lecturer_capacity
        self._total_project_capacity: int = int(math.ceil(1.1 * self._num_students))

        self._li: int = lower_bound # lower bound of student preference list
        self._lj: int = upper_bound # upper bound of student preference list

        self.student_tie_density = student_tie_density
        self.lecturer_tie_density = lecturer_tie_density

        self._reset_instance()


    def _reset_instance(self):
        # student -> [project preferences]
        self._sp = {
            f's{i}': [] for i in range(1, self._num_students + 1)
        }

        # project -> [capacity, lecturer, student]
        self._plc = {
            f'p{i}': [1, '', []] for i in range(1, self._num_projects + 1)
        }

        # lecturer -> [capacity, projects, students, max of all c_j, sum of all c_j]
        self._lp = {
            f'l{i}': [0, [], [], 0, 0] for i in range(1, self._num_lecturers + 1)
        }


    def _assign_project_lecturer(self, project, lecturer):
        self._plc[project][1] = lecturer
        self._lp[lecturer][1].append(project)
        self._lp[lecturer][2] += self._plc[project][2] # track all students
        self._lp[lecturer][4] += self._plc[project][0] # track sum of all c_j
        if self._plc[project][0] > self._lp[lecturer][3]: # track max of all c_j
            self._lp[lecturer][3] = self._plc[project][0]


    def _assign_using_density(self, pref_list, value, density):
        """
        Assigns the given value to the given preference list,
        according to the provided (tie) density.
        """
        if random.uniform(0, 1) > density:
            pref_list.append([value])
        else:
            pref_list[-1].append(value)


    def _generate_projects(self):
        """
        Generates project capacities for the SPA-ST problem.
        """
        project_list = list(self._plc.keys())
        if self._force_project_capacity:
            for project in self._plc:
                self._plc[project][0] = self._force_project_capacity
        else:
            for _ in range(self._total_project_capacity - self._num_projects):
                self._plc[random.choice(project_list)][0] += 1


    @abstractmethod
    def _generate_students(self):
        """
        Generates students for the SPA-ST problem.
        """
        raise NotImplementedError


    @abstractmethod
    def _generate_lecturers(self):
        """
        Generates lecturers for the SPA-ST problem.
        """
        raise NotImplementedError


    def generate_instance(self) -> None:
        """
        Generates an instance for the SPA-ST problem.
        Stores details in self._sp, self._plc, self._lp.
        """
        self._reset_instance()
        self._generate_projects()
        self._generate_students()
        self._generate_lecturers()


    def _tied_list_to_string(self, l: list[list[str]], delim: str = ' ') -> str:
        """
        Take in a list of lists of strings that represents a tied preference list,
        and return a string representation of the list

        :param l: a list of lists of strings
        :return: a string representation of the list
        """
        return delim.join(
            list(map(
                lambda s: str(s).replace(',', ''),
                [
                    x
                    if len(x := tuple(map(lambda x: int(x[1:]), p))) > 1
                    else x[0] for p in l
                ]
            ))
        )


    def write_instance_to_file(self, filename: str) -> None:
        """
        Writes instances to filename specified.
        """
        if filename.endswith('.txt'): delim = ' '
        elif filename.endswith('.csv'): delim = ','

        with open(filename, 'w') as f:
            f.write(delim.join(map(str, [self._num_students, self._num_projects, self._num_lecturers])) + '\n')

            # student index, preferences
            for student in self._sp:
                f.write(f"{student[1:]}{delim}{self._tied_list_to_string(self._sp[student], delim)}\n")

            # project index, capacity, lecturer
            for project in self._plc:
                f.write(delim.join(map(str, [project[1:], self._plc[project][0], self._plc[project][1][1:]])) + "\n")

            # lecturer index, capacity, preferences
            for lecturer in self._lp:
                f.write(f"{lecturer[1:]}{delim}{self._lp[lecturer][0]}{delim}{self._tied_list_to_string(self._lp[lecturer][2], delim)}\n")
