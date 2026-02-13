"""
For a fixed n1 and varying tie density and preference list length,
this module compares the matching sizes of strong and weak solvers for SPAST instances.
"""
import numpy as np
from pathlib import Path
from tqdm import tqdm

from concurrent.futures import ProcessPoolExecutor
from itertools import product
import os

from algmatch.stableMatchings.studentProjectAllocation.ties.spastStrongSolver import SPASTStrongSolver
from algmatch.stableMatchings.studentProjectAllocation.ties.spastWeakSolver import SPASTWeakSolver


def find_matching(solver, filename):
    s = solver(filename, output_flag=0)
    s.J.setParam("Threads", 1)
    s.solve()
    return s


def find_and_write(filename="instance.txt"):
    weak_solver = find_matching(SPASTWeakSolver, filename)
    strong_solver = find_matching(SPASTStrongSolver, filename)

    return weak_solver.assignments_as_dict(), strong_solver.assignments_as_dict()


NUM_STUDENTS = 25
ITERS = 100
CLUSTER_DIR="./"

def run_instance(sd: float, ld: float):
    sd, ld = round(sd, 2), round(ld, 2)
    for i in range(ITERS):
        filename = f"instance_{int(sd*100)}_{int(ld*100)}_{i}.txt"
        weak_soln, strong_soln = find_and_write(
            CLUSTER_DIR + "data/" + filename
        )

        with open(CLUSTER_DIR + "matchings/" + filename, "w") as f:
            f.write(f"filename: {filename}\n")
            f.write("weak solution:\n")
            f.write(str(weak_soln) if weak_soln is not None else "None")
            f.write("\n\nstrong solution:\n")
            f.write(str(strong_soln) if strong_soln is not None else "None")


if __name__ == "__main__":
    assert os.path.isdir(CLUSTER_DIR + "data"), "`data` directory must exist and be populated"
    assert os.path.isdir(CLUSTER_DIR + "results"), "`results` directory must exist and be populated"
    Path(CLUSTER_DIR + "matchings").mkdir(parents=True, exist_ok=True)

    grid = list(product(
        np.arange(0, 1, 0.1),
        np.arange(0, 1, 0.1)
    ))

    with ProcessPoolExecutor(max_workers=os.cpu_count()) as pool:
        for _ in tqdm(pool.map(run_instance, *zip(*grid))): pass
