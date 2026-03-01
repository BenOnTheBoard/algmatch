from matplotlib import pyplot as plt
import numpy as np
import inspect

from algmatch.stableMatchings.studentProjectAllocation.ties.experiments.strongProbabilityTiming import (
    GENERATORS,
    combination_generation
)

"""
For each file in RESULTS_DIR, plot a heatmap grid with
- tie density for lecturers as x-axis (second param)
- tie density for students as y-axis (first param)
- probability of stable matching existence

File format for filename:
    <n1>_<pref list length>_<student tie density>_<lecturer tie density>_<gen method>_results.txt
First line: <solution exists count>,<solution doesnt exist count>
Next ITERS lines:
    time taken in ns for each run
"""

RESULTS_DIR = "./results/"
ITERS = 25
OUTPUT_DIR = "./"

SDs = np.arange(0, 0.41, 0.05)
LDs = np.arange(0, 0.41, 0.05)
using_combination = lambda x: inspect.isfunction(x)
get_gen_name = lambda x, g: "SPASTIG_Combination" if using_combination(g) else str(x)
filename = lambda n1, sd, ld, gen_name: f"{RESULTS_DIR}{n1}_{n1 // 10}_{int(sd*100)}_{int(ld*100)}_{gen_name}_results.txt"

def plot_heatmap(n1):
    for generation_method in GENERATORS + [combination_generation]:
        # dummy initialisation
        generator = generation_method(
            num_students=100,
            lower_bound=10,
            upper_bound=10,
            num_projects=50,
            num_lecturers=20
        )
        generator_name = get_gen_name(generator, generation_method)
        print(generator_name)
        heatmap = np.zeros((len(SDs), len(LDs)))
        for i, sd in enumerate(SDs):
            for j, ld in enumerate(LDs):
                with open(filename(n1, sd, ld, generator_name), "r") as f:
                    heatmap[i, j] = float(f.readlines()[0].split(",")[0]) / ITERS

        X, Y = np.meshgrid(LDs, SDs)
        plt.pcolormesh(
            X, Y,
            heatmap,
            cmap="magma_r",
            vmin=0,
            vmax=1,
            shading="auto",
            edgecolor="k",
            linewidth=0.5
        )
        plt.xlabel("Lecturer Tie Density")
        plt.ylabel("Student Tie Density")
        plt.colorbar(label="Probability of Stable Matching Existence")
        plt.title(f"{generator_name} - Probability Heatmap for {n1} students")
        plt.savefig(f"{OUTPUT_DIR}heatmap_{generator_name}.jpg")
        plt.close()


if __name__ == "__main__":
    plot_heatmap(100)
