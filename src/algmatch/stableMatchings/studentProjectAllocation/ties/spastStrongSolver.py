"""
Using Gurobi Integer Programming solver to solve the SPA-ST problem.
"""

from collections import defaultdict
from tqdm import tqdm

import gurobipy as gp
from gurobipy import GRB

from algmatch.stableMatchings.studentProjectAllocation.ties.fileReaderIPModel import FileReaderIPModel as FileReader
from algmatch.stableMatchings.studentProjectAllocation.ties.entityPreferenceInstance import EntityPreferenceInstance as EPI
from algmatch.stableMatchings.studentProjectAllocation.ties.spastBruteforcer import SPASTBruteforcer as Brute
from algmatch.stableMatchings.studentProjectAllocation.ties.instanceGenerators import SPASTIG_Random


class GurobiSPAST:
    def __init__(self, filename: str, output_flag=1) -> None:
        self.filename = filename
        r = FileReader(filename)

        self._students = r.students
        self._projects = r.projects
        self._lecturers = r.lecturers

        self.J = gp.Model("SPAST")
        self.J.setParam('OutputFlag', output_flag)

        self.matching = defaultdict(str)


    def _matching_constraints(self) -> None:
        """
        Matching contraints

        x_{ij} in {0, 1} s.t. (1 <= i <= |S|, 1 <= j <= |P|)
        x_{ij} indicates whether s_i is assigned to p_j in a solution or not

        sum_{p_j in A_i}(x_{ij}) <= 1 for all i in {1, 2, ..., |S|} # student can be assigned to at most one project
        sum_{i=1}^{|S|}(x_{ij}) <= c_j for all j in {1, 2, ..., |P|} # project does not exceed capacity
        sum_{i=1}^{|S|} sum_{p_j in P_k} x_{ij} <= d_k for all k in {1, 2, ..., |L|} # lecturer does not exceed capacity
        """

        for student in self._students:
            sum_student_variables = gp.LinExpr()
            for project in self._students[student][1]:
                xij = self.J.addVar(lb=0.0, ub=1.0, obj=0.0, vtype=GRB.BINARY, name=f"{student} is assigned {project}")
                self._students[student][1][project] = xij
                sum_student_variables += xij

            # CONSTRAINT: student can be assigned to at most one project
            self.J.addConstr(sum_student_variables <= 1, f"Constraint (4.5) for {student}")

        for project in self._projects:
            total_project_capacity = gp.LinExpr()
            for student in self._students:
                if project in self._students[student][1]:
                    total_project_capacity += self._students[student][1][project]

            # CONSTRAINT: project does not exceed capacity
            self.J.addConstr(total_project_capacity <= self._projects[project][0], f"Total capacity constraint (4.6) for {project}")

        for lecturer in self._lecturers:
            total_lecturer_capacity = gp.LinExpr()
            for student in self._students:
                for project in self._students[student][1]:
                    if lecturer == self._projects[project][1]:
                        total_lecturer_capacity += self._students[student][1][project]

            # CONSTRAINT: lecturer does not exceed capacity
            self.J.addConstr(total_lecturer_capacity <= self._lecturers[lecturer][0], f"Total capacity constraint (4.7) for {lecturer}")


    def _get_outranked_entities(self, preference_list, entity, strict=False) -> list:
        """
        Get entities that outrank entity in preference list

        :param strict: if True, only return entities that strictly outrank entity
        """
        idx = 0
        p = preference_list[idx]
        outranked_projects = []
        while entity not in p:
            outranked_projects += p
            idx += 1
            p = preference_list[idx]
        
        outranked_projects += p if not strict else []
        return outranked_projects


    def _get_equal_entities(self, preference_list, entity) -> list:
        """
        Get entities that are equal to entity in preference list
        """
        for p in preference_list:
            if entity in p:
                return p
            

    def _P_k(self, l_k) -> list:
        """
        Return list of projects offered by lecturer l_k
        """
        return [
            project for project in self._projects if self._projects[project][1] == l_k
        ]
    

    def _L_k_j(self, l_k, p_j) -> list:
        """
        Return projected preference list of lecturer l_k for project p_j
        """
        Lkj = []
        for student_entity in self._lecturers[l_k][1]:
            if student_entity.isTie:
                projected_tie = [s for s in student_entity if p_j in self._students[s][1]]
                if len(projected_tie) > 1:
                    new_EPI = EPI(tuple(projected_tie))
                    Lkj.append(new_EPI)
                elif len(projected_tie) == 1:
                    Lkj.append(projected_tie[0])
            else:
                if p_j in self._students[student_entity][1]:
                    Lkj.append(student_entity)
        return Lkj


    def _theta(self, s_i, p_j) -> gp.LinExpr:
        """
        theta_{ij} = 1 - (sum of x_{ij'} over projects p_{j'} equal or higher than p_j in student's preference list)
        theta_{ij} = 1 iff student is unassigned or prefers p_j to M(s_i)
        """
        theta_ij = gp.LinExpr()
        sum_outranked_projects = gp.LinExpr()

        S_ij = self._get_outranked_entities(self._students[s_i][0], p_j)
        for p_jprime in S_ij:
            sum_outranked_projects += self._students[s_i][1][p_jprime]

        theta_ij.addConstant(1)
        theta_ij.add(sum_outranked_projects, -1)

        return theta_ij
    

    def _theta_star(self, s_i, p_j) -> gp.LinExpr:
        """
        theta_{ij} = (sum of x_{ij'} over projects p_{j'} equal to p_j in student's preference list) - x_{ij}
        theta_{ij} = 1 iff student is indifferent between p_j and M(s_i), where p_j not in M(s_i)
        """
        theta_star_ij = gp.LinExpr()
        sum_equal_projects = gp.LinExpr()

        S_star_ij = self._get_equal_entities(self._students[s_i][0], p_j)
        for p_jprime in S_star_ij:
            sum_equal_projects += self._students[s_i][1][p_jprime]

        theta_star_ij.add(sum_equal_projects)
        theta_star_ij.add(self._students[s_i][1][p_j], -1)

        return theta_star_ij
    

    def _get_project_occupancy(self, project) -> gp.LinExpr:
        """
        Get the occupancy of project p_j defined as
        sum_{i=1}^{|S|} x_{ij}
        """
        project_occupancy = gp.LinExpr()
        for student in self._students:
            if project in self._students[student][1]:
                project_occupancy += self._students[student][1][project]

        return project_occupancy


    def _get_lecturer_occupancy(self, lecturer) -> gp.LinExpr:
        """
        Get the occupancy of lecturer l_k defined as
        sum_{i=1}^{|S|} sum_{p_j in P_k} x_{ij}
        """
        lecturer_occupancy = gp.LinExpr()
        for project in self._P_k(lecturer):
            for student in self._students:
                if project in self._students[student][1]:
                    lecturer_occupancy += self._students[student][1][project]

        return lecturer_occupancy
    

    def _alpha(self, p_j) -> gp.Var:
        """
        alpha_j in {0, 1} s.t. (1 <= j <= |P|)
        alpha_j = 1 <= project p_j is undersubscribed
        """
        alpha_j = self.J.addVar(lb=0.0, ub=1.0, obj=0.0, vtype=GRB.BINARY, name=f"{p_j} is undersubscribed")
        c_j = self._projects[p_j][0]
        project_occupancy = self._get_project_occupancy(p_j)

        # CONSTRAINT: ensures p_j is not oversubscribed
        self.J.addConstr(c_j * alpha_j >= c_j - project_occupancy, f"Constraint (4.8) for {p_j}")
        return alpha_j


    def _beta(self, l_k) -> gp.Var:
        """
        beta_k in {0, 1} s.t. (1 <= k <= |L|)
        beta_k = 1 <= lecturer l_k is undersubscribed
        """
        beta_k = self.J.addVar(lb=0.0, ub=1.0, obj=0.0, vtype=GRB.BINARY, name=f"{l_k} is undersubscribed")
        d_k = self._lecturers[l_k][0]
        lecturer_occupancy = self._get_lecturer_occupancy(l_k)

        # CONSTRAINT: if l_k is undersubscribed in M, beta_k = 1
        self.J.addConstr(d_k * beta_k >= d_k - lecturer_occupancy, f"Constraint (4.9) for {l_k}")
        return beta_k

    
    def _eta(self, l_k) -> gp.Var:
        """
        eta_k in {0, 1} s.t. (1 <= k <= |L|)
        eta_k = 1 <= lecturer l_k is full
        """
        eta_k = self.J.addVar(lb=0.0, ub=1.0, obj=0.0, vtype=GRB.BINARY, name=f"{l_k} is full")
        d_k = self._lecturers[l_k][0]
        lecturer_occupancy = self._get_lecturer_occupancy(l_k)

        # CONSTRAINT: if l_k is full in M, eta_k = 1
        self.J.addConstr(d_k * eta_k >= 1 + lecturer_occupancy - d_k, f"Constraint (4.11) for {l_k}")
        return eta_k


    def _delta(self, s_i, l_k) -> gp.Var:
        """
        delta_{ik} in {0, 1} s.t. (1 <= i <= |S|, 1 <= k <= |L|)
        delta_{ik} = 1 <= s_i in M(l_k) or l_k prefers s_i to a worst student in M(l_k) or l_k is indifferent between them
        """
        delta_ik = self.J.addVar(lb=0.0, ub=1.0, obj=0.0, vtype=GRB.BINARY, name=f"{s_i} is assigned to {l_k}")
        d_k = self._lecturers[l_k][0]
        lecturer_occupancy = self._get_lecturer_occupancy(l_k)

        lecturer_preferred_occupancy = gp.LinExpr()
        D_ik = self._get_outranked_entities(self._lecturers[l_k][1], s_i, strict=True)

        for student in D_ik:
            for project in self._P_k(l_k):
                if project in self._students[student][1]:
                    lecturer_preferred_occupancy += self._students[student][1][project]

        # CONSTRAINT: if s_i in M(l_k) or l_k prefers s_i to a worst student in M(l_k)
        # or l_k is indifferent between them, delta_{ik} = 1
        self.J.addConstr(d_k * delta_ik >= lecturer_occupancy - lecturer_preferred_occupancy, f"Constraint (4.12) for {s_i} {l_k}")
        return delta_ik
    

    def _gamma(self, p_k) -> gp.Var:
        """
        gamma_j in {0, 1} s.t. (1 <= j <= |P|)
        gamma_j = 1 <= p_j is full
        """
        gamma_j = self.J.addVar(lb=0.0, ub=1.0, obj=0.0, vtype=GRB.BINARY, name=f"{p_k} is full")
        c_j = self._projects[p_k][0]
        project_occupancy = self._get_project_occupancy(p_k)

        # CONSTRAINT: if p_j is full in M, gamma_j = 1
        self.J.addConstr(c_j * gamma_j >= 1 + project_occupancy - c_j, f"Constraint (4.14) for {p_k}")
        return gamma_j
    

    def _lambda(self, s_i, p_j, l_k) -> gp.Var:
        """
        lambda_{ijk} in {0, 1} s.t. (1 <= i <= |S|, 1 <= j <= |P|, 1 <= k <= |L|)
        lambda_{ijk} = 1 <= l_k prefers s_i to a worst student in M(p_j) or l_k is indifferent between them
        """
        lambda_ijk = self.J.addVar(lb=0.0, ub=1.0, obj=0.0, vtype=GRB.BINARY, name=f"{l_k} prefers / indifferent to {s_i} to a worst student in M({p_j})")
        c_j = self._projects[p_j][0]
        project_occupancy = self._get_project_occupancy(p_j)

        project_preferred_occupancy = gp.LinExpr()
        T_ijk = self._get_outranked_entities(self._L_k_j(l_k, p_j), s_i, strict=True)
        for student in T_ijk:
            project_preferred_occupancy += self._students[student][1][p_j]

        # CONSTRAINT: if l_k prefers s_i to a worst student in M(p_j)
        # or l_k is indifferent between them, lambda_{ijk} = 1
        self.J.addConstr(c_j * lambda_ijk >= project_occupancy - project_preferred_occupancy, f"Constraint (4.15) for {s_i} {p_j} {l_k}")
        return lambda_ijk


    def _omega(self, s_i, l_k):
        omega_ik = gp.LinExpr()
        for project in self._P_k(l_k):
            if project in self._students[s_i][1]:
                omega_ik += self._students[s_i][1][project]

        return omega_ik
    

    def _mu(self, s_i, l_k) -> gp.Var:
        """
        mu_{ik} in {0, 1} s.t. (1 <= i <= |S|, 1 <= k <= |L|)
        mu_{ik} = 1 <= s_i in M(l_k) or l_k prefers s_i to a worst student in M(l_k)
        """
        mu_ik = self.J.addVar(lb=0.0, ub=1.0, obj=0.0, vtype=GRB.BINARY, name=f"{l_k} assigned to / prefers {s_i} to a worst student in M({l_k})")
        d_k = self._lecturers[l_k][0]
        lecturer_occupancy = self._get_lecturer_occupancy(l_k)
        omega_ik = self._omega(s_i, l_k)

        lecturer_preferred_occupancy = gp.LinExpr()
        D_star_ik = self._get_outranked_entities(self._lecturers[l_k][1], s_i)
        for student in D_star_ik:
            for project in self._P_k(l_k):
                if project in self._students[student][1]:
                    lecturer_preferred_occupancy += self._students[student][1][project]

        # CONSTRAINT: if s_i in M(l_k) or l_k prefers s_i to a worst student in M(l_k), mu_{ik} = 1
        self.J.addConstr(d_k * mu_ik >= omega_ik + lecturer_occupancy - lecturer_preferred_occupancy, f"Constraint (5.15) for {s_i} {l_k}")
        return mu_ik
    

    def _tau(self, s_i, p_j, l_k) -> gp.Var:
        """
        tau_{ijk} in {0, 1} s.t. (1 <= i <= |S|, 1 <= j <= |P|, 1 <= k <= |L|)
        tau_{ijk} = 1 <= l_k prefers s_i to a worst student in M(p_j)
        """
        tau_ijk = self.J.addVar(lb=0.0, ub=1.0, obj=0.0, vtype=GRB.BINARY, name=f"{l_k} prefers {s_i} to a worst student in M({p_j})")
        c_j = self._projects[p_j][0]
        project_occupancy = self._get_project_occupancy(p_j)

        project_preferred_occupancy = gp.LinExpr()
        T_star_ijk = self._get_outranked_entities(self._L_k_j(l_k, p_j), s_i)
        for student in T_star_ijk:
            project_preferred_occupancy += self._students[student][1][p_j]

        # CONSTRAINT: if l_k prefers s_i to a worst student in M(p_j), tau_{ijk} = 1
        self.J.addConstr(c_j * tau_ijk >= project_occupancy - project_preferred_occupancy, f"Constraint (5.17) for {s_i} {p_j} {l_k}")
        return tau_ijk

    
    def _blocking_pair_constraints(self) -> None:
        for s_i in self._students:
            for p_j in self._students[s_i][1]:
                l_k = self._projects[p_j][1]

                theta_ij = self._theta(s_i, p_j)
                theta_star_ij = self._theta_star(s_i, p_j)
                alpha_j = self._alpha(p_j)
                beta_k = self._beta(l_k)

                eta_k = self._eta(l_k)
                delta_ik = self._delta(s_i, l_k)

                gamma_j = self._gamma(p_j)
                lambda_ijk = self._lambda(s_i, p_j, l_k)

                mu_ik = self._mu(s_i, l_k)

                tau_ijk = self._tau(s_i, p_j, l_k)

                self.J.addConstr(theta_ij + alpha_j + beta_k <= 2, f"Blocking pair 1i for {s_i} and {p_j} (5.11)")
                self.J.addConstr(theta_ij + alpha_j + eta_k + delta_ik <= 3, f"Blocking pair 1ii for {s_i} and {p_j} (5.12)")
                self.J.addConstr(theta_ij + gamma_j + lambda_ijk <= 2, f"Blocking pair 1iii for {s_i} and {p_j} (5.13)")

                self.J.addConstr(theta_star_ij + alpha_j + beta_k <= 2, f"Blocking pair 2i for {s_i} and {p_j} (5.14)")
                self.J.addConstr(theta_star_ij + alpha_j + eta_k + mu_ik <= 3, f"Blocking pair 2ii for {s_i} and {p_j} (5.16)")
                self.J.addConstr(theta_star_ij + gamma_j + tau_ijk <= 2, f"Blocking pair 2iii for {s_i} and {p_j} (5.18)")


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
        self._matching_constraints()
        self._blocking_pair_constraints()
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

        G = GurobiSPAST("instance.txt", output_flag=0)
        G.solve()
        G_answer = G.assignments_as_dict()

        B = Brute(filename="instance.txt", stability_type="strong")
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