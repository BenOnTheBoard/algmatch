from matplotlib import pyplot as plt
import numpy as np
import inspect
from pathlib import Path

from algmatch.stableMatchings.studentProjectAllocation.ties.experiments.strongProbabilityTiming import (
    GENERATORS,
    combination_generation
)

ALL_GENERATORS = GENERATORS + [combination_generation]
ITERS = 25
DUMMY_ARGS = {
    "num_students": 100,
    "lower_bound": 10,
    "upper_bound": 10,
    "num_projects": 50,
    "num_lecturers": 20
}

SDs = np.arange(0, 0.051, 0.005)
LDs = np.arange(0, 0.051, 0.005)
using_combination = lambda x: inspect.isfunction(x)
get_gen_name = lambda x, g: "SPASTIG_Combination" if using_combination(g) else str(x)
generator_name = lambda x: get_gen_name(x(**DUMMY_ARGS), x)
generator_short_name = lambda x: generator_name(x).split("_")[-1]
filename = lambda n1, sd, ld, gen_name, res_dir: res_dir + "_".join([
    str(n1),
    str(max(5, n1 // 10)),
    str(round(sd, 4)),
    str(round(ld, 4)),
    gen_name,
    "results.txt"
])

def plot_heatmap(n1):
    res_dir = f"{ALL_RESULTS_DIR}/results/"
    for gen in ALL_GENERATORS:
        heatmap = np.zeros((len(SDs), len(LDs)))

        for i, sd in enumerate(SDs):
            for j, ld in enumerate(LDs):
                with open(filename(n1, sd, ld, generator_name(gen), res_dir), "r") as f:
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
        plt.title(f"Probability Heatmap ({n1} students)\n{generator_name(gen)}")
        plt.savefig(f"{OUTPUT_DIR}heatmap_{generator_short_name(gen)}_{n1}.jpg")
        plt.close()


def plot_avg_times(n1):
    res_dir = f"{ALL_RESULTS_DIR}/results/"
    for gen in ALL_GENERATORS:
        avg_times = np.zeros((len(SDs), len(LDs)))
        highest = -1

        for i, sd in enumerate(SDs):
            for j, ld in enumerate(LDs):
                with open(filename(n1, sd, ld, generator_name(gen), res_dir), "r") as f:
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
        plt.title(f"Average Time ({n1} students)\n{generator_name(gen)}")
        plt.savefig(f"{OUTPUT_DIR}avg_time_{generator_short_name(gen)}_{n1}.jpg")
        plt.close()


def plot_box_plot(n1, sd, ld):
    res_dir = f"{ALL_RESULTS_DIR}/results/"
    times = []
    for gen in ALL_GENERATORS:
        with open(filename(n1, sd, ld, generator_name(gen), res_dir), "r") as f:
            times.append(list(map(lambda x: 1e-9 * float(x), f.readlines()[1:])))

    plt.figure(figsize=(len(times), 8))
    plt.boxplot(times)
    plt.xticks(
        range(1, len(times) + 1),
        list(map(generator_short_name, ALL_GENERATORS)),
        rotation=90
    )
    plt.ylabel("Time (seconds)")
    plt.title(f"Box Plot ({n1} students, SD={sd}, LD={ld})")
    plt.tight_layout()
    plt.savefig(f"{OUTPUT_DIR}box_plot_times_{n1}_{int(sd*100)}_{int(ld*100)}.jpg")


def plot_line_graph(sd, ld):
    """
    Plots line graph of avg time against n1
    for all generation methods, on one graph
    """
    get_results_dir = lambda n1: f"{ALL_RESULTS_DIR}/small_results_{n1}/results/"
    output_dir = "./probabilityResults/"
    n1_values = list(range(10, 101, 10))
    for gen in ALL_GENERATORS:
        times = []
        for n1 in n1_values:
            with open(filename(n1, sd, ld, generator_name(gen), get_results_dir(n1)), "r") as f:
                data = list(map(lambda x: 1e-9 * float(x), f.readlines()[1:]))
                times.append(sum(data) / len(data))
        plt.plot(n1_values, times, label=generator_short_name(gen))
    plt.xlabel("Number of Students")
    plt.ylabel("Time (seconds)")
    plt.title(f"Average time per generation method ({int(sd*100)}% SD, {int(ld*100)}% LD)")
    plt.legend()
    plt.savefig(f"{output_dir}line_times_{int(sd*100)}_{int(ld*100)}.jpg")
    plt.close()


if __name__ == "__main__":
    N1 = 100
    ALL_RESULTS_DIR = "/home/varad/Desktop/programming/algmatch/experimentResults/small_results/"
    OUTPUT_DIR = f"./probabilityResults/results_{N1}/"
    Path(OUTPUT_DIR).mkdir(parents=True, exist_ok=True)
    # plot_heatmap(N1)
    # plot_avg_times(N1)
    # plot_box_plot(N1, 0.05, 0.05)
    plot_line_graph(0.05, 0.05)
