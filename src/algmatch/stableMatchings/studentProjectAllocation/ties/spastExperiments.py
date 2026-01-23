from pathlib import Path
from tqdm import tqdm
import time
import numpy as np

from spastSolver import GurobiSPAST
from algmatch.stableMatchings.studentProjectAllocation.ties.instanceGenerators import (
    SPASTIG_Abstract,
    SPASTIG_Random,
    SPASTIG_Euclidean,
    SPASTIG_ReverseEuclidean,
    SPASTIG_ExpectationsEuclidean,
    SPASTIG_FameEuclidean,
    SPASTIG_Attributes,
    SPASTIG_FameEuclideanExtended
)

def run_experiment(
    generation_method: SPASTIG_Abstract,
    num_students: int,
    lower_bound: int,
    upper_bound: int,
    num_projects: int,
    num_lecturers: int,
    foldername: str,
    filename_prefix: str,
    runs: int = 100,
    **kwargs
):
    s = generation_method(
        num_students,
        lower_bound,
        upper_bound,
        num_projects,
        num_lecturers,
        **kwargs
    )
    EXPERIMENTS_FOLDER = "experiments"
    Path(f"{EXPERIMENTS_FOLDER}/{foldername}").mkdir(parents=True, exist_ok=True)
    time_results = np.zeros(runs)

    for i in tqdm(range(runs)):
        filename = f"{EXPERIMENTS_FOLDER}/{foldername}/{filename_prefix}_{i}.txt"
        s.generate_instance()
        s.write_instance_to_file(filename)

        start_time = time.time()
        G = GurobiSPAST(filename, output_flag=0)
        G.solve()
        end_time = time.time()
        time_results[i] = end_time - start_time

    with open(f"{EXPERIMENTS_FOLDER}/results_{foldername}.txt", "w") as f:
        print(f"""
Folder name: {foldername}
Average time taken (seconds): {time_results.mean()}
Params:
    generation_method: {generation_method}
    num_students: {num_students}
        lower_bound: {lower_bound}
        upper_bound: {upper_bound}
    num_projects: {num_projects}
    num_lecturers: {num_lecturers}
    runs: {runs}
    kwargs: {kwargs}
    """, file=f)


if __name__ == "__main__":
    n1 = 100
    run_experiment(
        SPASTIG_Random,
        n1, 1, n1 // 2,
        n1 // 2, n1 // 5,
        "random",
        "random100",
        100
    )
