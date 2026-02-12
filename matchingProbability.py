from tqdm import tqdm
from pathlib import Path
import numpy as np

from concurrent.futures import ProcessPoolExecutor
from itertools import product
import os

from algmatch.stableMatchings.studentProjectAllocation.ties.spastStrongSolver import SPASTStrongSolver
from algmatch.stableMatchings.studentProjectAllocation.ties.spastSuperStudentOptimal import SPASTSuperStudentOptimal
from algmatch.stableMatchings.studentProjectAllocation.ties.instanceGenerators.random import SPASTIG_Random

CLUSTER_DIR = "./"


def run_experiment(
    num_students,
    pref_list_length,
    student_tie_density,
    lecturer_tie_density,
    iters
):
    results = {
        "super_exists": 0,
        "strong_exists": 0,
        "both_exist": 0,
        "neither_exist": 0
    }
    Path(CLUSTER_DIR + "data").mkdir(parents=True, exist_ok=True)
    Path(CLUSTER_DIR + "results").mkdir(parents=True, exist_ok=True)
    foldername = f"{num_students}_{pref_list_length}_{int(student_tie_density*100)}_{int(lecturer_tie_density*100)}"
    Path(CLUSTER_DIR + f"data/{foldername}").mkdir(parents=True, exist_ok=True)

    for i in range(iters):
        filename = CLUSTER_DIR + f"data/{foldername}/instance_{i}.txt"
        generator = SPASTIG_Random(
            num_students=num_students,
            lower_bound=pref_list_length,
            upper_bound=pref_list_length,
            num_projects=num_students // 2,
            num_lecturers=num_students // 5,
            student_tie_density=student_tie_density,
            lecturer_tie_density=lecturer_tie_density,
        )
        generator.generate_instance()
        generator.write_instance_to_file(filename)

        spast_super = SPASTSuperStudentOptimal(filename)
        spast_super.run()

        spast_strong = SPASTStrongSolver(filename, output_flag=0)
        spast_strong.J.setParam("Threads", 1)
        spast_strong.solve()

        if spast_super.is_stable:
            if spast_strong.assignments_as_dict():
                results["both_exist"] += 1
            else:
                results["super_exists"] += 1
        elif spast_strong.assignments_as_dict():
            results["strong_exists"] += 1
        else:
            results["neither_exist"] += 1

    with open(CLUSTER_DIR + f"results/{foldername}_results.txt", "w") as f:
        f.write(f"""Iters: {iters}
Params:
    Num students: {num_students}
    Preference list length: {pref_list_length}
    Student tie density: {student_tie_density}
    Lecturer tie density: {lecturer_tie_density}

Results:
    Super exists: {results["super_exists"]}
    Strong exists: {results["strong_exists"]}
    Both exist: {results["both_exist"]}
    Neither exist: {results["neither_exist"]}

{results["both_exist"]},{results["super_exists"]},{results["strong_exists"]},{results["neither_exist"]}""")


def run_instance(n1: int, sd: float, ld: float):
    sd, ld = round(sd, 2), round(ld, 2)
    run_experiment(
        n1, n1 // 2, sd, ld, 100
    )


if __name__ == "__main__":
    grid = list(product(
        range(100, 1001, 100),
        np.arange(0, 1, 0.1),
        np.arange(0, 1, 0.1)
    ))

    with ProcessPoolExecutor(max_workers=os.cpu_count()) as pool:
        for _ in tqdm(pool.map(run_instance, *zip(*grid))): pass
