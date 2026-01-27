import numpy as np

from algmatch.stableMatchings.studentProjectAllocation.ties.spastExperiments import run_experiment
from algmatch.stableMatchings.studentProjectAllocation.ties.instanceGenerators import SPASTIG_ReverseEuclidean

for n1 in range(100, 1001, 100):
    for sd in np.arange(0, 1, 0.1):
        for ld in np.arange(0, 1, 0.1):
            sd, ld = round(sd, 2), round(ld, 2)
            run_experiment(
                SPASTIG_ReverseEuclidean,
                n1, 1, n1 // 2,
                n1 // 2, n1 // 5,
                "reverse",
                f"reverse_{n1}_{sd}_{ld}",
                root_folder="results",
                runs=100,
                student_tie_density=sd,
                lecturer_tie_density=ld,
            )