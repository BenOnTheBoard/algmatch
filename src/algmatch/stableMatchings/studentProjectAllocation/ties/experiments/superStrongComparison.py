"""
For a given n1, sd, ld, keep generating instances
and check if a super stable matching exists.
If it does not, check if a strongly stable matching exists.
Record probability of strongly stable matching existing.
Record total number of instances generated.
"""
import time
import os
import numpy as np
from tqdm import tqdm
from concurrent.futures import ProcessPoolExecutor
from itertools import product

from algmatch.stableMatchings.studentProjectAllocation.ties.spastStrongSolver import SPASTStrongSolver
from algmatch.stableMatchings.studentProjectAllocation.ties.spastSuperStudentOptimal import SPASTSuperStudentOptimal
from algmatch.stableMatchings.studentProjectAllocation.ties.instanceGenerators import SPASTIG_ExpectationsEuclidean

ITERS = 100
FILENAME = "instance.txt"
CLUSTER_DIR = os.path.join(os.getenv("CLUSTER_DIR", "./"), "superStrongComparison/")


def compare_matching_strengths(n1, sd, ld):
    sd, ld = round(sd, 4), round(ld, 4)
    pref_list_length = max(5, n1 // 10)
    generator = SPASTIG_ExpectationsEuclidean(
        num_students=n1,
        lower_bound=pref_list_length,
        upper_bound=pref_list_length,
        num_projects=n1 // 2,
        num_lecturers=n1 // 5,
        student_tie_density=sd,
        lecturer_tie_density=ld,
    )
    super_count = 0
    strong_count = 0
    start_time = time.perf_counter_ns()

    for _ in range(ITERS):
        generator.generate_instance()
        generator.write_instance_to_file(FILENAME)

        super_solver = SPASTSuperStudentOptimal(filename=FILENAME)
        super_solver.run()
        if super_solver.is_stable:
            super_count += 1
        else:
            strong_solver = SPASTStrongSolver(filename=FILENAME, output_flag=0)
            strong_solver.J.setParam("Threads", 1)
            strong_solver.solve()
            if strong_solver.assignments_as_dict():
                strong_count += 1

    time_taken = (time.perf_counter_ns() - start_time) / 1e9
    neither_count = ITERS - super_count - strong_count
    with open(os.path.join(CLUSTER_DIR, f"results_{n1}_{sd}_{ld}.txt"), "w") as f:
        f.write(f"""Out of {ITERS} generated instances,
    {super_count} had super stable matchings (and hence strongly stable matchings),
    {ITERS - super_count} had no super stable matchings,
        of which {strong_count} had strongly stable matchings, and
    {neither_count} had neither strong nor super stable matchings;
for n1 = {n1}, sd = {sd}, ld = {ld}.
Total time taken: {time_taken}s

P(super),P(strong),P(neither),P(strong|no super)
{super_count / ITERS},{strong_count / ITERS},{neither_count / ITERS},{strong_count / (ITERS - super_count)}""")


if __name__ == "__main__":
    grid = list(product(
        range(50, 301, 25),
        np.arange(0.01, 0.031, 0.005),
        np.arange(0.01, 0.031, 0.005),
    ))

    with ProcessPoolExecutor(max_workers=os.cpu_count()) as pool:
        for _ in tqdm(pool.map(compare_matching_strengths, *zip(*grid))): pass
