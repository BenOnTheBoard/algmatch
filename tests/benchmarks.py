from statistics import stdev, mean
from time import perf_counter_ns

from algmatch.hospitalResidentsProblem import HospitalResidentsProblem
from tests.HRTests.utils.instanceGenerator import HRInstanceGenerator

from algmatch.stableMarriageProblem import StableMarriageProblem
from tests.SMTests.utils.instanceGenerator import SMInstanceGenerator

from algmatch.studentProjectAllocation import StudentProjectAllocation
from tests.SPASTests.utils.instanceGenerator import SPAInstanceGenerator


def show_results(data):
    time1, time2, name1, name2, data, reps = data
    if len(data) == 4:
        total1, total2, lower, upper = data
        res = f"""
        Total {name1}: {total1}
        Total {name2}: {total2}
        Preference list length lower bound: {lower}
        Preference list length upper bound: {upper}
        """
    else:
        total, lower, upper = data
        res = f"""
        Total {name1}: {total}
        Lower project bound: {lower}
        Upper project bound: {upper}
        """

    print(
        res
        + f"""
        Repetitions: {reps}

        {name1}-optimal solver:
            average: {mean(time1) / 1_000_000:.2f} ms
            std.dev.: {stdev(time1) / 1_000_000:.2f} ms
        
        {name2}-optimal solver:
            average: {mean(time2) / 1_000_000:.2f} ms
            std.dev.: {stdev(time2) / 1_000_000:.2f} ms
    """
    )


def time_solver(solver, dictionary, optimised_side):
    optimal_solver = solver(dictionary=dictionary, optimised_side=optimised_side)
    start = perf_counter_ns()
    optimal_solver.get_stable_matching()
    end = perf_counter_ns()

    return end - start


def benchmark(IGData, IG, reps, solver, optimised_sides):
    bencher_ig = IG(*IGData)

    times1 = []
    times2 = []

    for _ in range(reps):
        instance = bencher_ig.generate_instance_no_ties()

        times1.append(time_solver(solver, instance, optimised_sides[0]))
        times2.append(time_solver(solver, instance, optimised_sides[1]))

    show_results([times1, times2, optimised_sides[0], optimised_sides[1], IGData, reps])


def main():
    print("### Timing HR:")
    benchmark(
        [75, 75, 75, 75],
        HRInstanceGenerator,
        1_000,
        HospitalResidentsProblem,
        ["residents", "hospitals"],
    )

    print("### Timing SM:")
    benchmark(
        [75, 75, 75, 75],
        SMInstanceGenerator,
        1_000,
        StableMarriageProblem,
        ["men", "women"],
    )

    print("### Timing SPA:")
    benchmark(
        [50, 20, 25],
        SPAInstanceGenerator,
        1_000,
        StudentProjectAllocation,
        ["students", "lecturers"],
    )


if __name__ == "__main__":
    main()
