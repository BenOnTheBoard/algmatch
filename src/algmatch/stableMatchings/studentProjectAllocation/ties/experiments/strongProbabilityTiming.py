from tqdm import tqdm
from pathlib import Path
import numpy as np
from random import choice

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


def combination_generation(*args):
    return choice(GENERATORS)(*args)


def run_experiment(
    num_students,
    pref_list_length,
    student_tie_density,
    lecturer_tie_density,
    iters,
    generation_method
):
    results = {
        "soln_exi": 0,
        "soln_dne": 0
    }
    generator = generation_method(
        num_students=num_students,
        lower_bound=pref_list_length,
        upper_bound=pref_list_length,
        num_projects=num_students // 2,
        num_lecturers=num_students // 5,
        student_tie_density=student_tie_density,
        lecturer_tie_density=lecturer_tie_density,
    )

    foldername = '_'.join([
        str(num_students), str(pref_list_length),
        str(int(student_tie_density*100)),
        str(int(lecturer_tie_density*100)),
        str(generator) if isinstance(generator, SPASTIG_Abstract) else "SPASTIG_Combination"
    ])
    Path(CLUSTER_DIR + f"data/{foldername}").mkdir(parents=True, exist_ok=True)

    for i in range(iters):
        filename = CLUSTER_DIR + f"data/{foldername}/instance_{i}.txt"
        generator.generate_instance()
        generator.write_instance_to_file(filename)

        spast_strong = SPASTStrongSolver(filename, output_flag=0)
        spast_strong.J.setParam("Threads", 1)
        spast_strong.solve()

        if spast_strong.assignments_as_dict():
            results["soln_exi"] += 1
        else:
            results["soln_dne"] += 1

    with open(CLUSTER_DIR + f"results/{foldername}_results.txt", "w") as f:
        f.write(f"""Iters: {iters}
Params:
    Num students: {num_students}
    Preference list length: {pref_list_length}
    Student tie density: {student_tie_density}
    Lecturer tie density: {lecturer_tie_density}

Results:
    Solution exists: {results["soln_exi"]}
    Solution does not exist: {results["soln_dne"]}

{results["soln_exi"]},{results["soln_dne"]}
""")

def run_instance(n1: int, sd: float, ld: float, gen: SPASTIG_Abstract):
    sd, ld = round(sd, 2), round(ld, 2)
    run_experiment(
        n1, n1 // 10, sd, ld, 100, gen
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
