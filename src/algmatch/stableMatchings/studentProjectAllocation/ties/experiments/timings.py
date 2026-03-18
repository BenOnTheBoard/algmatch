import time
from tqdm import tqdm
from matplotlib import pyplot as plt

from algmatch.stableMatchings.studentProjectAllocation.ties.spastStrongSolver import SPASTStrongSolver
from algmatch.stableMatchings.studentProjectAllocation.ties.instanceGenerators import SPASTIG_Random

RUNS = 20
RESULTS = {}

for n1 in tqdm(range(10, 101, 10)):
    RESULTS[n1] = []

    for _ in tqdm(range(RUNS)):
        S = SPASTIG_Random(
            num_students=n1,
            lower_bound=min(10, n1//2),
            upper_bound=min(10, n1//2),
            num_projects=n1 // 2,
            num_lecturers=n1 // 5
        )
        S.generate_instance()
        S.write_instance_to_file("instance.txt")

        G = SPASTStrongSolver("instance.txt", output_flag=0)
        start = time.perf_counter_ns()
        G.solve()
        end = time.perf_counter_ns()
        RESULTS[n1].append(end - start)

plt.plot(list(RESULTS.keys()), [1e-9 * sum(RESULTS[n]) / RUNS for n in RESULTS])
plt.xlabel('Number of Students')
plt.ylabel('Average Time (seconds)')
plt.title(f'Average Time over {RUNS} iterations vs Number of Students')
plt.savefig("res.jpg")
