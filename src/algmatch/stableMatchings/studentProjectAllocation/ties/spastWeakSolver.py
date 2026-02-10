"""
Using Gurobi Integer Programming solver to solve the SPA-ST problem.
This time with weak stability.
"""

import gurobipy as gp
from gurobipy import GRB

from algmatch.stableMatchings.studentProjectAllocation.ties.spastAbstractSolver import SPASTAbstractSolver


class SPASTWeakSolver(SPASTAbstractSolver):
    def __init__(self, filename: str, output_flag=1) -> None:
        super().__init__(filename, "SPAST_Weak", output_flag)


    def _matching_constraints(self) -> None:
        for s_i in self._students:
            sum_student_variables = gp.LinExpr()
            for p_j in self._students[s_i][1]:
                xij = self.J.addVar(lb=0.0, ub=1.0, obj=0.0, vtype=GRB.BINARY, name=f"{s_i} is assigned {p_j}")
                self._students[s_i][1][p_j] = xij
                sum_student_variables += xij
                if not self._entity_list_ranks_element(self._students[s_i][0], p_j):
                    self.J.addConstr(self._students[s_i][1][p_j] <= 0, f"Constraint 1. for {s_i}, {p_j}")

            self.J.addConstr(sum_student_variables <= 1, f"Single assignment constraint for {s_i}")

        for p_j in self._projects:
            total_project_capacity = gp.LinExpr()
            for s_i in self._students:
                total_project_capacity += self._students[s_i][1][p_j]

            self.J.addConstr(total_project_capacity <= self._projects[p_j][0], f"Total capacity constraint for {p_j}")

        for l_k in self._lecturers:
            total_lecturer_capacity = gp.LinExpr()
            for s_i in self._students:
                for p_j in self._students[s_i][1]:
                    if l_k == self._projects[p_j][1]:
                        total_lecturer_capacity += self._students[s_i][1][p_j]

            self.J.addConstr(total_lecturer_capacity <= self._lecturers[l_k][0], f"Total capacity constraint for {l_k}")


    def _blocking_pair_constraints(self) -> None:
        for s_i in self._students:
            sum_student_variables = gp.LinExpr()
            for p_j in self._projects:
                l_k = self._projects[p_j][1]

                alpha_ij = self.J.addVar(lb=0.0, ub=1.0, obj=0.0, vtype=GRB.BINARY, name=f"alpha_{s_i}{p_j}")
                beta_ij = self.J.addVar(lb=0.0, ub=1.0, obj=0.0, vtype=GRB.BINARY, name=f"beta_{s_i}{p_j}")

                if self._entity_list_ranks_element(self._students[s_i][0], p_j):
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
                    s_u for s_u in self._get_outranked_entities(self._lecturers[l_k][1], s_i)
                    if self._entity_list_ranks_element(self._students[s_u][0], p_j)
                )
                T_ijk.discard(s_i)
                constraint_sum = gp.LinExpr()
                for s_u in T_ijk:
                    constraint_sum += self._students[s_u][1][p_j]

                self.J.addConstr(constraint_sum >= self._projects[p_j][0] * beta_ij, f"Constraint 7. for {s_i}, {p_j}")

            self.J.addConstr(sum_student_variables <= 1, f"Constraint 2. for {s_i}")


    def _objective_function(self) -> None:
        all_xij = gp.LinExpr()
        for s_i in self._students:
            for x_ij in self._students[s_i][1].values():
                    all_xij += x_ij

        self.J.setObjective(all_xij, GRB.MAXIMIZE)


    def solve(self) -> None:
        self._matching_constraints()
        self._blocking_pair_constraints()
        self._objective_function()

        self.J.optimize()