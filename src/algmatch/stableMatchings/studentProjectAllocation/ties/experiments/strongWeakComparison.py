"""
For a fixed n1 and varying tie density and preference list length,
this module compares the matching sizes of strong and weak solvers for SPAST instances.
"""
import time
import numpy as np
from pathlib import Path
from tqdm import tqdm

from concurrent.futures import ProcessPoolExecutor
from itertools import product
import os

from algmatch.stableMatchings.studentProjectAllocation.ties.spastStrongSolver import SPASTStrongSolver
from algmatch.stableMatchings.studentProjectAllocation.ties.spastWeakSolver import SPASTWeakSolver
from algmatch.stableMatchings.studentProjectAllocation.ties.instanceGenerators.random import SPASTIG_Random


def time_solver(solver, filename) -> tuple[float, dict[str, str]]:
    s = solver(filename, output_flag=0)
    s.J.setParam("Threads", 1)
    start = time.perf_counter_ns()
    s.solve()
    time_taken = time.perf_counter_ns() - start
    answer = s.assignments_as_dict()
    return time_taken, answer


def find_matching_size(matching: dict[str, str]) -> int:
    return sum(int(bool(v)) for v in matching.values()) if matching else 0


def compare_matching_sizes(
    num_students,
    student_tie_density,
    lecturer_tie_density,
    pref_list_length,
    filename="instance.txt"
) -> tuple[float, int, float, int]:
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

    weak_time, weak_answer = time_solver(SPASTWeakSolver, filename)
    strong_time, strong_answer = time_solver(SPASTStrongSolver, filename)

    return (
        weak_time, find_matching_size(weak_answer),
        strong_time, find_matching_size(strong_answer)
    )


NUM_STUDENTS = 25
ITERS = 100
CLUSTER_DIR="./"

def run_instance(sd: float, ld: float):
    times: list[tuple[float, int, float, int]] = []
    sd, ld = round(sd, 2), round(ld, 2)
    for i in range(ITERS):
        times.append(
            compare_matching_sizes(
                NUM_STUDENTS,
                sd,
                ld,
                NUM_STUDENTS // 2,
                CLUSTER_DIR + f"data/instance_{int(sd*100)}_{int(ld*100)}_{i}.txt"
            )
        )

    with open(CLUSTER_DIR + f"results/instance_{int(sd*100)}_{int(ld*100)}.csv", "w") as f:
        f.write("Weak Time (ns),Weak Size,Strong Time (ns),Strong Size,Time Difference (ns)\n")
        for weak_time, weak_size, strong_time, strong_size in times:
            f.write(f"{weak_time},{weak_size},{strong_time},{strong_size},{weak_time - strong_time}\n")

if __name__ == "__main__":
    Path(CLUSTER_DIR + "data").mkdir(parents=True, exist_ok=True)
    Path(CLUSTER_DIR + "results").mkdir(parents=True, exist_ok=True)

    grid = list(product(
        np.arange(0, 1, 0.1),
        np.arange(0, 1, 0.1)
    ))

    with ProcessPoolExecutor(max_workers=os.cpu_count()) as pool:
        for _ in tqdm(pool.map(run_instance, *zip(*grid))): pass
