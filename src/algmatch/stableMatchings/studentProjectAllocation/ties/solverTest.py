from tqdm import tqdm

from algmatch.stableMatchings.studentProjectAllocation.ties.spastBruteforcer import SPASTBruteforcer as Brute
from algmatch.stableMatchings.studentProjectAllocation.ties.instanceGenerators import SPASTIG_Random

from algmatch.stableMatchings.studentProjectAllocation.ties.spastStrongSolver import SPASTStrongSolver
from algmatch.stableMatchings.studentProjectAllocation.ties.spastWeakSolver import SPASTWeakSolver

def matching_size(matching):
    return sum(int(bool(v)) for v in matching.values())


def test(Solver, stability_type):
    s = SPASTIG_Random(
        num_students=6,
        lower_bound=0,
        upper_bound=4,
        num_projects=4,
        num_lecturers=2
    )
    runs = 100

    results = {
        "right": 0,
        "wrong": 0,
        "maximal": 0
    }

    for _ in tqdm(range(runs)):
        s.generate_instance()
        s.write_instance_to_file('instance.txt')

        G = Solver("instance.txt", output_flag=0)
        G.solve()
        G_answer = G.assignments_as_dict()

        B = Brute(filename="instance.txt", stability_type=stability_type)
        B.choose()
        answer_list = B.get_ssm_list()

        if G_answer is None:
            if not answer_list:
                results["right"] += 1
                results["maximal"] += 1
            else:
                results["wrong"] += 1
        elif G_answer in answer_list:
            results["right"] += 1
            if matching_size(G_answer) == max(map(matching_size, answer_list)):
                results["maximal"] += 1
        else:
            results["wrong"] += 1

    message = []
    message.append(f"Test Type: {stability_type} stability")
    message.append("")
    message.append("Instances:")
    message.append(f"  num_students\t= {s._num_students}")
    message.append(f"  lower_bound\t= {s._li}")
    message.append(f"  upper_bound\t= {s._lj}")
    message.append(f"  num_projects\t= {s._num_projects}")
    message.append(f"  num_lecturers\t= {s._num_lecturers}")
    message.append("")
    message.append("Model Test Results:")
    message.append(f"  Right: {results['right']}, {100*results['right']/runs:.2f}%")
    if results['right'] > 0:
        message.append(f"    Maximal matching found: {results['maximal']}, {100*results['maximal']/results['right']:.2f}%")
    message.append(f"  Wrong: {results['wrong']}, {100*results['wrong']/runs}%")
    message.append("")

    print("\n\t".join(message))


if __name__ == "__main__":
    test(SPASTWeakSolver, "weak")
    test(SPASTStrongSolver, "strong")
