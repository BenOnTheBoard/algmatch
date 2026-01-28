"""
Using Gurobi Integer Programming solver to solve the SPA-ST problem.
This time with weak stability.
"""

from collections import defaultdict
from tqdm import tqdm

import gurobipy as gp
from gurobipy import GRB

from algmatch.stableMatchings.studentProjectAllocation.ties.fileReaderIPModel import FileReaderIPModel as FileReader
from algmatch.stableMatchings.studentProjectAllocation.ties.spastBruteforcer import SPASTBruteforcer as Brute
from algmatch.stableMatchings.studentProjectAllocation.ties.instanceGenerators import SPASTIG_Random


class SPASTWeakSolver:
    def __init__(self, filename: str, output_flag=1) -> None:
        self.filename = filename
        r = FileReader(filename)

        self._students = r.students
        self._projects = r.projects
        self._lecturers = r.lecturers

        self.J = gp.Model("SPAST")
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


    def _constraints(self) -> None:
        for s_i in self._students:
            sum_student_variables = gp.LinExpr()
            for p_j in self._projects:
                l_k = self._projects[p_j][1]

                x_ij = self.J.addVar(lb=0.0, ub=1.0, obj=0.0, vtype=GRB.BINARY, name=f"{s_i} is assigned to {p_j}")
                self._students[s_i][1][p_j] = x_ij
                sum_student_variables += x_ij
                if p_j not in self._students[s_i][1]:
                    self.J.addConstr(x_ij <= 0, f"Constraint 1. for {s_i}, {p_j}")

                alpha_ij = self.J.addVar(lb=0.0, ub=1.0, obj=0.0, vtype=GRB.BINARY, name=f"alpha_{s_i}{p_j}")
                beta_ij = self.J.addVar(lb=0.0, ub=1.0, obj=0.0, vtype=GRB.BINARY, name=f"beta_{s_i}{p_j}")

                outranked_sum = gp.LinExpr()
                for p_r in self._get_outranked_entities(self._students[s_i][0], p_j):
                    outranked_sum += self._students[s_i][1][p_r]
                    
                self.J.addConstr(1 - outranked_sum <= alpha_ij + beta_ij, f"Constraint 5. for {s_i}, {p_j}")

                T_ik = set(self._get_outranked_entities(self._lecturers[l_k][1], s_i))
                T_ik.discard(s_i)
                P_k = [p_r for p_r in self._projects if self._projects[p_r][1] == l_k]
                constraint_sum = gp.LinExpr()
                for s_u in T_ik:
                    for p_r in P_k:
                        constraint_sum += self._students[s_u][1][p_r]

                self.J.addConstr(constraint_sum >= self._lecturers[l_k][0] * alpha_ij, f"Constraint 6. for {s_i}, {p_j}")

                T_ijk = set(
                    s_u for s_u in self._get_outranked_entities(self._lecturers[l_k][1], s_i) if p_j in self._students[s_u][1]
                )
                T_ijk.discard(s_i)
                constraint_sum = gp.LinExpr()
                for s_u in T_ijk:
                    constraint_sum += self._students[s_u][1][p_j]

                self.J.addConstr(constraint_sum >= self._projects[p_j][0] * beta_ij, f"Constraint 7. for {s_i}, {p_j}")

            self.J.addConstr(sum_student_variables <= 1, f"Constraint 2. for {s_i}")

        for p_j in self._projects:
            sum_student_variables = gp.LinExpr()
            for s_i in self._students:
                sum_student_variables += self._students[s_i][1][p_j]

            self.J.addConstr(sum_student_variables <= self._projects[p_j][0], f"Constraint 3. for {p_j}")

        for l_k in self._lecturers:
            sum_student_variables = gp.LinExpr()
            for s_i in self._students:
                P_k = [p_r for p_r in self._projects if self._projects[p_r][1] == l_k]
                for p_j in P_k:
                    sum_student_variables += self._students[s_i][1][p_j]
            
            self.J.addConstr(sum_student_variables <= self._lecturers[l_k][0], f"Constraint 4. for {l_k}")


    def _objective_function(self) -> None:
        all_xij = gp.LinExpr()
        for student in self._students:
            for x_ij in self._students[student][1].values():
                    all_xij += x_ij

        self.J.setObjective(all_xij, GRB.MAXIMIZE)

    
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
    
    def assignments_as_dict(self) -> dict:
        if self.J.Status != GRB.OPTIMAL:
            return None

        assignments = {}
        for student in self._students:
            assignments[student] = ""
            for project, xij in self._students[student][1].items():
                if xij.x == 1:
                    assignments[student] = project
        return assignments


    def solve(self) -> None:
        self._constraints()
        self._objective_function()

        self.J.optimize()


if __name__ == "__main__":
    s = SPASTIG_Random(
        num_students=5,
        lower_bound=0,
        upper_bound=3,
        num_projects=3,
        num_lecturers=1
    )
    runs = 1_000

    results = {"right":0, "wrong":0}

    for _ in tqdm(range(runs)):
        s.generate_instance()
        s.write_instance_to_file('instance.txt')

        G = SPASTWeakSolver("instance.txt", output_flag=0)
        G.solve()
        G_answer = G.assignments_as_dict()

        B = Brute(filename="instance.txt", stability_type="weak")
        B.choose()
        answer_list = B.get_ssm_list()

        if not answer_list and G_answer is None:
            results["right"] += 1
        elif G_answer in answer_list:
            results["right"] += 1
        else:
            results["wrong"] += 1

    print(f"""
          Model Test Results:
            Right: {results["right"]}, {100*results["right"]/runs}%
            Wrong: {results["wrong"]}, {100*results["wrong"]/runs}%
    """)