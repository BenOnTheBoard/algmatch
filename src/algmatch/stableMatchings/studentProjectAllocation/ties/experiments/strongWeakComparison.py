"""
For a fixed n1 and varying tie density and preference list length,
this module compares the matching sizes of strong and weak solvers for SPAST instances.
"""
import time
from pathlib import Path
from tqdm import tqdm
from dataclasses import dataclass
import json
import os

from concurrent.futures import ProcessPoolExecutor
from itertools import product

from algmatch.stableMatchings.studentProjectAllocation.ties.spastStrongSolver import SPASTStrongSolver
from algmatch.stableMatchings.studentProjectAllocation.ties.spastWeakSolver import SPASTWeakSolver
from algmatch.stableMatchings.studentProjectAllocation.ties.instanceGenerators import SPASTIG_ExpectationsEuclidean


@dataclass
class MatchingInfo:
    time: float
    size: int
    rank: list[int]


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


def find_rank(
    matching: dict[str, str] | None,
    student_preferences: dict[str, list[str]],
    num_projects: int,
) -> list[int]:
    rank = [0] * num_projects

    if matching is None:
        return rank

    for student, project in matching.items():
        if project:
            idx = 0
            while project not in student_preferences[student][idx]:
                idx += 1
            rank[idx] += 1

    return rank


def set_info(time, matching: dict[str, str], student_preferences: dict[str, list[str]], num_projects: int):
    return MatchingInfo(
        time,
        find_matching_size(matching),
        find_rank(matching, student_preferences, num_projects),
    )


def compare_matching_sizes(
    num_students,
    student_tie_density,
    lecturer_tie_density,
    pref_list_length,
    filename="instance.txt"
) -> tuple[MatchingInfo, MatchingInfo]:
    num_projects = num_students // 2
    generator = SPASTIG_ExpectationsEuclidean(
        num_students=num_students,
        lower_bound=pref_list_length,
        upper_bound=pref_list_length,
        num_projects=num_projects,
        num_lecturers=num_students // 5,
        student_tie_density=student_tie_density,
        lecturer_tie_density=lecturer_tie_density,
    )
    generator.generate_instance()
    generator.write_instance_to_file(filename)
    student_prefs = generator.get_student_preferences()

    weak_time, weak_answer = time_solver(SPASTWeakSolver, filename)
    strong_time, strong_answer = time_solver(SPASTStrongSolver, filename)

    return (
        set_info(weak_time, weak_answer, student_prefs, num_projects),
        set_info(strong_time, strong_answer, student_prefs, num_projects)
    )


ITERS = 100
CLUSTER_DIR = os.getenv("CLUSTER_DIR", "./") + "strongWeakComparison/"

def run_instance(n1: int, sd: float, ld: float):
    times: list[tuple[MatchingInfo, MatchingInfo]] = []
    sd, ld = round(sd, 2), round(ld, 2)
    for i in range(ITERS):
        times.append(
            compare_matching_sizes(
                n1,
                sd,
                ld,
                max(5, n1 // 10),
                CLUSTER_DIR + f"data/{n1}_{int(sd*100)}_{int(ld*100)}_instance_{i}.txt"
            )
        )

    instance_data = {
        "n1": n1,
        "sd": sd,
        "ld": ld,
        "times": [
            {
                "weak": {
                    "time": weak_info.time,
                    "size": weak_info.size,
                    "rank": weak_info.rank,
                },
                "strong": {
                    "time": strong_info.time,
                    "size": strong_info.size,
                    "rank": strong_info.rank,
                },
                "time_diff": weak_info.time - strong_info.time,
            }
            for weak_info, strong_info in times
        ],
    }
    with open(CLUSTER_DIR + f"results/{n1}_{int(sd*100)}_{int(ld*100)}.json", "w") as f:
        json.dump(instance_data, f)

if __name__ == "__main__":
    Path(CLUSTER_DIR + "data").mkdir(parents=True, exist_ok=True)
    Path(CLUSTER_DIR + "results").mkdir(parents=True, exist_ok=True)

    grid = list(product(
        range(10, 101, 10),
        [0.01], [0.01]
    ))

    with ProcessPoolExecutor(max_workers=os.cpu_count()) as pool:
        for _ in tqdm(pool.map(run_instance, *zip(*grid))): pass
