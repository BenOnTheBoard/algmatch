class AbstractVerifier:
    def __init__(self, problem, sides, gen, gen_args, brute_force, stability_type=None):
        self.Problem = problem
        self.sides = sides
        self.BruteForce = brute_force
        self.stability_type = stability_type
        self.gen = gen(*gen_args)
        self.current_instance = {}

    def generate_instance(self):
        self.current_instance = self.gen.generate_instance()

    def verify_instance(self):
        # optimal and pessimal from man/resident/student side
        if self.stability_type is not None:
            bruteforcer = self.BruteForce(
                dictionary=self.current_instance, stability_type=self.stability_type
            )
            optimal_solver = self.Problem(
                dictionary=self.current_instance,
                optimised_side=self.sides[0],
                stability_type=self.stability_type,
            )
            pessimal_solver = self.Problem(
                dictionary=self.current_instance,
                optimised_side=self.sides[1],
                stability_type=self.stability_type,
            )
        else:
            bruteforcer = self.BruteForce(dictionary=self.current_instance)
            optimal_solver = self.Problem(
                dictionary=self.current_instance, optimised_side=self.sides[0]
            )
            pessimal_solver = self.Problem(
                dictionary=self.current_instance, optimised_side=self.sides[1]
            )

        bruteforcer.find_stable_matchings()
        m_0 = optimal_solver.get_stable_matching()
        m_z = pessimal_solver.get_stable_matching()

        if not bruteforcer.stable_matching_list:
            if m_z is None and m_0 is None:
                return True
            else:
                return False

        if m_z not in bruteforcer.stable_matching_list:
            return False
        if m_0 not in bruteforcer.stable_matching_list:
            return False
        return True

    def run(self):
        raise NotImplementedError("No method for processing instances")

    def show_results(self):
        raise NotImplementedError("No method for outputing the results")
