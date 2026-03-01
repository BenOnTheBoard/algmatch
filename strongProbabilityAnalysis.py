from matplotlib import pyplot as plt
import numpy as np
import inspect

from algmatch.stableMatchings.studentProjectAllocation.ties.experiments.strongProbabilityTiming import (
    GENERATORS,
    combination_generation
)

RESULTS_DIR = "./results/"
ITERS = 25
OUTPUT_DIR = "./"
DUMMY_ARGS = {
    "num_students": 100,
    "lower_bound": 10,
    "upper_bound": 10,
    "num_projects": 50,
    "num_lecturers": 20
}

SDs = np.arange(0, 0.41, 0.05)
LDs = np.arange(0, 0.41, 0.05)
using_combination = lambda x: inspect.isfunction(x)
get_gen_name = lambda x, g: "SPASTIG_Combination" if using_combination(g) else str(x)
filename = lambda n1, sd, ld, gen_name: f"{RESULTS_DIR}{n1}_{n1 // 10}_{int(sd*100)}_{int(ld*100)}_{gen_name}_results.txt"

def plot_heatmap(n1):
    for generation_method in GENERATORS + [combination_generation]:
        # dummy initialisation
        generator = generation_method(**DUMMY_ARGS)
        generator_name = get_gen_name(generator, generation_method)
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
        plt.title(f"Probability Heatmap ({n1} students)\n{generator_name}")
        plt.savefig(f"{OUTPUT_DIR}heatmap_{generator_name}.jpg")
        plt.close()


def plot_avg_times(n1):
    for generation_method in GENERATORS + [combination_generation]:
        # dummy initialisation
        generator = generation_method(**DUMMY_ARGS)
        generator_name = get_gen_name(generator, generation_method)
        avg_times = np.zeros((len(SDs), len(LDs)))
        highest = -1

        for i, sd in enumerate(SDs):
            for j, ld in enumerate(LDs):
                with open(filename(n1, sd, ld, generator_name), "r") as f:
                    times = map(float, f.readlines()[1:])
                    avg_times[i, j] = 1e-9 * sum(times) / ITERS
                    highest = max(highest, avg_times[i, j])

        X, Y = np.meshgrid(LDs, SDs)
        plt.pcolormesh(
            X, Y,
            avg_times,
            cmap="magma_r",
            vmin=0,
            vmax=highest,
            shading="auto",
            edgecolor="k",
            linewidth=0.5
        )
        plt.xlabel("Lecturer Tie Density")
        plt.ylabel("Student Tie Density")
        plt.colorbar(label="Average Time (seconds)")
        plt.title(f"Average Time ({n1} students)\n{generator_name}")
        plt.savefig(f"{OUTPUT_DIR}avg_time_{generator_name}.jpg")
        plt.close()

if __name__ == "__main__":
    plot_heatmap(100)
    plot_avg_times(100)
