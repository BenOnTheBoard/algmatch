from pathlib import Path
from tqdm import tqdm
import time
import numpy as np
import os

from spastSolver import GurobiSPAST
from algmatch.stableMatchings.studentProjectAllocation.ties.instanceGenerators import (
    SPASTIG_Abstract,
    SPASTIG_Euclidean,
)

def run_experiment(
    generation_method: SPASTIG_Abstract,
    num_students: int,
    lower_bound: int,
    upper_bound: int,
    num_projects: int,
    num_lecturers: int,
    experiment_folder: str,
    filename_prefix: str,
    root_folder: str = "experiments",
    runs: int = 100,
    save_data: bool = True,
    save_results: bool = True,
    **kwargs
):
    s = generation_method(
        num_students = num_students,
        lower_bound = lower_bound,
        upper_bound = upper_bound,
        num_projects = num_projects,
        num_lecturers = num_lecturers,
        **kwargs
    )
    base_folder = f"{root_folder}/{experiment_folder}"
    data_folder = f"{base_folder}_data"
    results_folder = f"{base_folder}_results"
    Path(data_folder).mkdir(parents=True, exist_ok=True)
    Path(results_folder).mkdir(parents=True, exist_ok=True)
    time_results = np.zeros(runs)

    for i in tqdm(range(runs)):
        filename = f"{data_folder}/{filename_prefix}{'_'+str(i) if save_data else ''}.txt"
        s.generate_instance()
        s.write_instance_to_file(filename)

        start_time = time.time()
        G = GurobiSPAST(filename, output_flag=0)
        G.solve()
        end_time = time.time()
        time_results[i] = end_time - start_time

    if not save_data:
        for file in os.listdir(data_folder):
            os.remove(os.path.join(data_folder, file))
        Path(data_folder).rmdir()

    if save_results:
        with open(f"{root_folder}/{experiment_folder}_results/results_{experiment_folder}_{filename_prefix}.txt", "w") as f:
            print(f"""
Folder name: {experiment_folder}
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
        SPASTIG_Euclidean,
        n1, 1, n1 // 2,
        n1 // 2, n1 // 5,
        "random",
        "random100",
        runs = 100
    )
