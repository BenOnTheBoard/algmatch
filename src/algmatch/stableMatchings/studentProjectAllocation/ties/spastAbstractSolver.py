"""
Using Gurobi Integer Programming solver to solve the SPA-ST problem.
"""

from collections import defaultdict
from abc import ABC, abstractmethod

import gurobipy as gp
from gurobipy import GRB

from algmatch.stableMatchings.studentProjectAllocation.ties.fileReaderIPModel import FileReaderIPModel as FileReader


class SPASTAbstractSolver(ABC):
    def __init__(self, filename: str, model_name="SPAST", output_flag=1) -> None:
        self.filename = filename
        r = FileReader(filename)

        self._students = r.students
        self._projects = r.projects
        self._lecturers = r.lecturers

        self.J = gp.Model(model_name)
        self.J.setParam('OutputFlag', output_flag)

        self.matching = defaultdict(str)


    def _get_outranked_entities(self, preference_list, entity, strict=False) -> list:
        """
        Get entities that outrank entity in preference list

        :param strict: if True, only return entities that strictly outrank entity
        """
        if len(preference_list) == 0: return []

        idx = 0
        p = preference_list[idx]
        outranked_projects = []
        while entity not in p:
            outranked_projects += p
            idx += 1
            if idx == len(preference_list): return outranked_projects
            p = preference_list[idx]

        outranked_projects += p if not strict else []
        return outranked_projects


    @abstractmethod
    def _objective_function(self) -> None:
        raise NotImplementedError("Objective function not implemented")


    def display_assignments(self) -> bool:
        # assumes model has been solved
        if self.J.Status != GRB.OPTIMAL:
            print("\nNo solution found. ILP written to spast.ilp file.")
            self.J.computeIIS()
            self.J.write("spast.ilp")
            return False

        for student in self._students:
            for project, xij in self._students[student][1].items():
                if xij.x == 1:
                    print(f"{student} -> {project}")

        return True


    def assignments_as_dict(self) -> dict | None:
        if self.J.Status != GRB.OPTIMAL:
            return None

        assignments = {}
        for student in self._students:
            assignments[student] = ""
            for project, xij in self._students[student][1].items():
                if xij.x == 1:
                    assignments[student] = project
        return assignments


    @abstractmethod
    def solve(self) -> None:
        raise NotImplementedError("Solve function not implemented")
