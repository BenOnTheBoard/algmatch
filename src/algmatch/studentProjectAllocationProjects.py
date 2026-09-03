"""
Class to provide interface for the SPA-P stable matching algorithm.
Also provides class for running several iterations, as well as configuring different variables.
"""

import os
import argparse
from tqdm import tqdm

from algmatch.stableMatchings.studentProjectAllocation.SPA_P.instanceGenerators import (
    SPAPIG_Abstract,
    SPAPIG_Random,
    SPAPIG_Euclidean,
    SPAPIG_ReverseEuclidean,
    SPAPIG_ExpectationsEuclidean,
    SPAPIG_FameEuclidean,
    SPAPIG_Attributes,
    SPAPIG_FameEuclideanExtended,
)

from algmatch.stableMatchings.studentProjectAllocation.SPA_P.SPAPSolver import (
    GurobiSPAP,
)
from algmatch.stableMatchings.studentProjectAllocation.SPA_P.checkStability import (
    StabilityChecker,
)


class StudentProjectAllocationProjectsSingle:
    def __init__(
        self,
        filename: str | None = None,
        output: str | None = None,
        output_flag: bool = True,
    ) -> None:
        """
        Initialise the SPA-P algorithm.

        :param filename: str, optional, default=None, the path to the file to read in the preferences from.
        :param output: str, optional, default=None, the path to the file to write the output to. Will print to console if None.

        :param output_flag: boolean, optional, default=True, the flag to determine whether to output the Gurobi solver output.
        """
        assert filename is not None, "Filename must be provided"

        self.filename = os.path.join(os.getcwd(), filename)

        self.output_file = (
            os.path.join(os.getcwd(), output) if output is not None else None
        )
        if self.output_file:
            if output.endswith(".txt"):
                self.delim = " "
            elif output.endswith(".csv"):
                self.delim = ","
        else:
            self.delim = ","  # assume csv

        self.solver = GurobiSPAP(filename=filename, output_flag=int(output_flag))

    def get_stable_matching(self) -> dict | str:
        """
        Get the stable matching for the Student Project Allocation algorithm.
        Also writes the output to file or console, as specified.

        :return: dict, the stable matching.
        """
        self.solver.solve()

        result = "\n".join(
            [f"{s[1:]}{self.delim}{p[1:]}" for s, p in self.solver.matching.items()]
        )
        print(
            result,
            file=None if self.output_file is None else open(self.output_file, "w"),
        )

        checker = StabilityChecker(self.solver)

        return (
            self.solver.matching
            if checker.check_stability()
            else "Matching is not stable."
        )


class StudentProjectAllocationProjectsMultiple:
    def __init__(
        self,
        instance_generator: SPAPIG_Abstract = None,
        instance_generator_args: dict = {},
        iters: int = 1,
        students: int = 5,
        lower_bound: int = 1,
        upper_bound: int = 3,
        projects: int = 10,
        project_capacity: int = 0,
        lecturers: int = 5,
        lecturer_capacity: int = 0,
        instance_folder: str = "instances/",
        solutions_folder: str = "solutions/",
        output_flag: bool = True,
        file_extension: str = "csv",
    ):
        """
        Run several iterations of the SPA-P algorithm.

        :param instance_generator: SPAPIG_Abstract, optional, default=SPAPIG_Random, what instance generator to use.
        :param instance_generator_args: dict, optional, default={}, the keyword arguments for the instance generator.
        :param iters: int, optional, default=1, the number of iterations to run the SPA-P algorithm for.
        :param students: int, optional, default=5, the number of students.
        :param lower_bound: int, optional, default=1, the lower bound of projects a student can rank.
        :param upper_bound: int, optional, default=3, the upper bound of projects a student can rank.
        :param projects: int, optional, default=10, the number of projects.
        :param project_capacity: int, optional, default=0, the capacity of all projects. If 0, capacity is random.
        :param lecturers: int, optional, default=5, the number of lecturers.
        :param lecturer_capacity: int, optional, default=0, the capacity of all lecturers. If 0, capacity is random.
        :param instance_folder: str, optional, default="instances/", the folder to save the instances to.
        :param solutions_folder: str, optional, default="solutions/", the folder to save the solutions to.
        :param output_flag: bool, optional, default=True, the flag to determine whether to output the Gurobi solver output.
        :param file_extension: str, optional, default='csv', what type of file to save instances and solutions to.
        """

        assert lower_bound <= upper_bound, (
            "Lower bound must be less than or equal to upper bound."
        )
        assert upper_bound <= projects, (
            "Upper bound must be less than or equal to the number of projects."
        )

        assert file_extension in ["csv", "txt"], (
            "File extension must be either 'csv' or 'txt'."
        )

        self.iters = iters
        self.num_students = students
        self.lower_bound = lower_bound
        self.upper_bound = upper_bound

        self.projects = projects
        self.project_capacity = project_capacity
        self.lecturers = lecturers
        self.lecturer_capacity = lecturer_capacity

        self.instance_folder = os.path.join(os.getcwd(), instance_folder)
        self.solutions_folder = os.path.join(os.getcwd(), solutions_folder)

        if not os.path.exists(self.instance_folder):
            os.makedirs(self.instance_folder)

        if not os.path.exists(self.solutions_folder):
            os.makedirs(self.solutions_folder)

        self.output_flag = int(output_flag)
        self.file_extension = file_extension
        self.delim = "," if file_extension == "csv" else " "

        if instance_generator is None:
            instance_generator = SPAPIG_Random

        self.IG = instance_generator(
            **instance_generator_args,
            num_students=students,
            lower_bound=lower_bound,
            upper_bound=upper_bound,
            num_projects=projects,
            force_project_capacity=project_capacity,
            num_lecturers=lecturers,
            force_lecturer_capacity=lecturer_capacity,
        )

    def _save_instance(self, filename: str) -> None:
        self.IG.generate_instance()
        self.IG.write_instance_to_file(filename)

    def _write_solution(self, matching: dict, filename: str) -> None:
        with open(filename, "w") as f:
            for student in matching:
                f.write(f"{student[1:]}{self.delim}{matching[student][1:]}\n")

    def run(self) -> None:
        """
        Runs solver for number of iterations specified.
        """
        print(f"Running {self.iters} iterations of SPA-P algorithm.")

        for i in tqdm(range(self.iters)):
            filename = self.instance_folder + f"instance_{i}.{self.file_extension}"
            self._save_instance(filename)

            solver = GurobiSPAP(filename=filename, output_flag=self.output_flag)
            solver.solve()
            checker = StabilityChecker(solver)
            is_stable = checker.check_stability()

            if is_stable:
                self._write_solution(
                    solver.matching,
                    self.solutions_folder + f"solution_{i}.{self.file_extension}",
                )
            else:
                print(f"Instance {i} is not stable.")


def main():

    def help_msg():
        return """
        Usage: python3 main.py [--single | --multiple] [options]

        Run the SPA-P algorithm for a single instance:
            python3 studentProjectAllocationProjects.py --single --filename FILENAME --output OUTPUT --output_flag OUTPUT_FLAG

        Run the SPA-P algorithm for multiple instances:
            python3 studentProjectAllocationProjects.py --multiple --iters ITERS --students STUDENTS 
                            [--lower_bound LOWER_BOUND --upper_bound UPPER_BOUND | --length LENGTH] 
                            --projects PROJECTS --force_project_capacity CAPACITY
                            --lecturers LECTURERS --force_lecturer_capacity CAPACITY
                            --instance_folder INSTANCE_FOLDER --solutions_folder SOLUTIONS_FOLDER 
                            --output_flag OUTPUT_FLAG --file_extension EXTENSION
                            --instance_generator GENERATOR_NAME --instance_generator_args arg1=val1 arg2=val2 ...
        """

    IG_arg_types = (
        {"num_dimensions": int}
        | {
            elt: float
            for elt in [
                "prop_s",
                "prop_l",
                "max_fame",
                "max_fame_student",
                "max_fame_lecturer",
                "stdev",
            ]
        }
        | {"": str}
    )

    def parse_pair(pair):
        key, value = pair.split("=")
        try:
            return key, IG_arg_types[key](value)
        except KeyError:
            print(f"Unrecognised argument: {key}")
            exit(1)

    parser = argparse.ArgumentParser(
        description="Run the SPA-P algorithm.", usage=help_msg()
    )

    parser.add_argument(
        "--single",
        action="store_true",
        help="Run the SPA-P algorithm for a single instance.",
    )

    parser.add_argument(
        "--filename",
        type=str,
        help="The filename of the instance to run the SPA-P algorithm on.",
    )
    parser.add_argument(
        "--output", type=str, help="The filename to write the output to."
    )

    parser.add_argument(
        "--multiple",
        action="store_true",
        help="Run the SPA-P algorithm for multiple instances.",
    )

    parser.add_argument(
        "--iters",
        type=int,
        default=1,
        help="The number of iterations to run the SPA-P algorithm for.",
    )
    parser.add_argument(
        "--students", type=int, default=5, help="The number of students."
    )
    parser.add_argument(
        "--lower_bound",
        type=int,
        help="The lower bound of the number of projects a student can rank.",
    )
    parser.add_argument(
        "--upper_bound",
        type=int,
        help="The upper bound of the number of projects a student can rank.",
    )
    parser.add_argument(
        "--length",
        type=int,
        help="The fixed length of the number of projects a student can rank.",
    )
    parser.add_argument(
        "--projects", type=int, default=10, help="The number of projects."
    )
    parser.add_argument(
        "--force_project_capacity",
        type=int,
        default=0,
        help="The capacity of all projects. If 0, capacity is random.",
    )
    parser.add_argument(
        "--lecturers", type=int, default=5, help="The number of lecturers."
    )
    parser.add_argument(
        "--force_lecturer_capacity",
        type=int,
        default=0,
        help="The capacity of all lecturers. If 0, capacity is random.",
    )
    parser.add_argument(
        "--instance_folder",
        type=str,
        default="instances/",
        help="The folder to save the instances to.",
    )
    parser.add_argument(
        "--solutions_folder",
        type=str,
        default="solutions/",
        help="The folder to save the solutions to.",
    )
    parser.add_argument(
        "--output_flag",
        action="store_true",
        help="The flag to determine whether to output the Gurobi solver output.",
    )
    parser.add_argument(
        "--file_extension",
        type=str,
        default="csv",
        help="What type of file to write the output to.",
    )
    parser.add_argument(
        "--instance_generator",
        type=str,
        default="random",
        help="The instance generator to use.",
    )
    parser.add_argument(
        "--instance_generator_args",
        type=parse_pair,
        default="=",
        help="The keyword arguments for the instance generator.",
        nargs="+",
    )

    args = parser.parse_args()

    if not any([args.single, args.multiple]) or all([args.single, args.multiple]):
        parser.print_help()
        print("Please specify either --single or --multiple and not both.")
        return

    if args.multiple:
        if any([args.filename, args.output]):
            parser.print_help()
            print(
                "Please do not specify --filename or --output for multiple instances."
            )
            return

        if not any([args.lower_bound, args.upper_bound, args.length]):
            parser.print_help()
            print(
                "Please specify either --lower_bound and --upper_bound or --length for multiple instances and not both."
            )
            return

        if args.length:
            if any([args.lower_bound, args.upper_bound]):
                parser.print_help()
                print(
                    "Please specify either --lower_bound and --upper_bound or --length for multiple instances and not both."
                )
                return

    valid_instance_generators = {
        "random": SPAPIG_Random,
        "euclidean": SPAPIG_Euclidean,
        "reverse_euclidean": SPAPIG_ReverseEuclidean,
        "expectations_euclidean": SPAPIG_ExpectationsEuclidean,
        "fame_euclidean": SPAPIG_FameEuclidean,
        "fame_euclidean_extended": SPAPIG_FameEuclideanExtended,
        "attributes": SPAPIG_Attributes,
    }

    if args.single:
        spa = StudentProjectAllocationProjectsSingle(
            filename=args.filename, output=args.output, output_flag=args.output_flag
        )
        spa.get_stable_matching()

    elif args.multiple:
        if args.length:
            lower_bound, upper_bound = args.length, args.length
        else:
            lower_bound, upper_bound = args.lower_bound, args.upper_bound

        if args.instance_generator not in valid_instance_generators:
            parser.print_help()
            print("Please specify a valid instance generator name.")
            print("Valid instance generator names:")
            [print(f"\t> {elt}") for elt in valid_instance_generators.keys()]
            return

        instance_generator = valid_instance_generators[args.instance_generator]
        instance_generator_args = (
            {key: value for key, value in args.instance_generator_args}
            if args.instance_generator_args != ("", "")
            else {}
        )

        spa = StudentProjectAllocationProjectsMultiple(
            instance_generator=instance_generator,
            instance_generator_args=instance_generator_args,
            iters=args.iters,
            students=args.students,
            lower_bound=lower_bound,
            upper_bound=upper_bound,
            projects=args.projects,
            project_capacity=args.force_project_capacity,
            lecturers=args.lecturers,
            lecturer_capacity=args.force_lecturer_capacity,
            instance_folder=args.instance_folder,
            solutions_folder=args.solutions_folder,
            output_flag=args.output_flag,
            file_extension=args.file_extension,
        )
        spa.run()


if __name__ == "__main__":
    main()
