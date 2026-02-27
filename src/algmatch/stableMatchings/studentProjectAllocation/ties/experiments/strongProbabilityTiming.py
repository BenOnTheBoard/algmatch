from tqdm import tqdm
from pathlib import Path
import numpy as np
from random import choice
import inspect
from time import perf_counter_ns

from concurrent.futures import ProcessPoolExecutor
from itertools import product
import os

from algmatch.stableMatchings.studentProjectAllocation.ties.spastAbstract import SPASTAbstract
from algmatch.stableMatchings.studentProjectAllocation.ties.spastStrongSolver import SPASTStrongSolver
from algmatch.stableMatchings.studentProjectAllocation.ties.spastSuperStudentOptimal import SPASTSuperStudentOptimal
from algmatch.stableMatchings.studentProjectAllocation.ties.instanceGenerators import (
    SPASTIG_Abstract,
    SPASTIG_Attributes,
    SPASTIG_Euclidean,
    SPASTIG_ExpectationsEuclidean,
    SPASTIG_FameEuclidean,
    SPASTIG_FameEuclideanExtended,
    SPASTIG_Random,
    SPASTIG_ReverseEuclidean
)

CLUSTER_DIR = "./"
GENERATORS = [
    SPASTIG_Attributes,
    SPASTIG_Euclidean,
    SPASTIG_ExpectationsEuclidean,
    SPASTIG_FameEuclidean,
    SPASTIG_FameEuclideanExtended,
    SPASTIG_Random,
    SPASTIG_ReverseEuclidean,
]
ITERS = 100


def combination_generation(*args, **kwargs):
    return choice(GENERATORS)(*args, **kwargs)


def run_experiment(
    num_students,
    pref_list_length,
    student_tie_density,
    lecturer_tie_density,
    iters,
    generation_method
):
    def _init_gen_method():
        return generation_method(
            num_students=num_students,
            lower_bound=pref_list_length,
            upper_bound=pref_list_length,
            num_projects=num_students // 2,
            num_lecturers=num_students // 5,
            student_tie_density=student_tie_density,
            lecturer_tie_density=lecturer_tie_density,
        )

    results = {
        "soln_exi": 0,
        "soln_dne": 0,
        "times": []
    }
    generator = _init_gen_method()
    using_combination = inspect.isfunction(generation_method)
    generator_name = "SPASTIG_Combination" if using_combination else str(generator)

    foldername = '_'.join([
        str(num_students), str(pref_list_length),
        str(int(student_tie_density*100)),
        str(int(lecturer_tie_density*100)),
        generator_name
    ])
    Path(CLUSTER_DIR + f"data/{foldername}").mkdir(parents=True, exist_ok=True)

    for i in range(iters):
        filename = CLUSTER_DIR + f"data/{foldername}/instance_{i}.txt"

        if using_combination:
            generator = _init_gen_method()

        generator.generate_instance()
        generator.write_instance_to_file(filename)
        with open(filename, "a") as f:
            f.write(str(generator))

        spast_strong = SPASTStrongSolver(filename, output_flag=0)
        spast_strong.J.setParam("Threads", 1)
        start = perf_counter_ns()
        spast_strong.solve()
        end = perf_counter_ns()
        results["times"].append(end - start)

        if spast_strong.assignments_as_dict():
            results["soln_exi"] += 1
        else:
            results["soln_dne"] += 1

    with open(CLUSTER_DIR + f"results/{foldername}_results.txt", "w") as f:
        f.write(f"{results['soln_exi']},{results['soln_dne']}\n")
        for time in results["times"]:
            f.write(f"{time}\n")

def run_instance(n1: int, sd: float, ld: float, gen: SPASTIG_Abstract):
    sd, ld = round(sd, 2), round(ld, 2)
    run_experiment(
        n1, n1 // 10, sd, ld, ITERS, gen
    )


if __name__ == "__main__":
    grid = list(product(
        range(100, 1001, 100),
        np.arange(0, 0.41, 0.05),
        np.arange(0, 0.41, 0.05),
        GENERATORS + [combination_generation]
    ))
    Path(CLUSTER_DIR + "data").mkdir(parents=True, exist_ok=True)
    Path(CLUSTER_DIR + "results").mkdir(parents=True, exist_ok=True)

    with ProcessPoolExecutor(max_workers=os.cpu_count()) as pool:
        for _ in tqdm(pool.map(run_instance, *zip(*grid))): pass
