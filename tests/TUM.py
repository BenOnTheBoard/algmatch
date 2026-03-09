from itertools import combinations
import numpy as np
from tqdm import tqdm

from algmatch.stableMatchings.studentProjectAllocation.ties.spastSolver import (
    GurobiSPAST,
)
from algmatch.stableMatchings.studentProjectAllocation.ties.spastGenerator import (
    SPASTGen,
)


def is_TUM(A):
    rows, cols = A.shape
    for size in range(1, min(rows, cols) + 1):
        for row_indices in combinations(range(rows), size):
            for col_indices in combinations(range(cols), size):
                submatrix = A[np.ix_(row_indices, col_indices)]
                det = np.linalg.det(submatrix)
                if det not in {0, 1, -1}:
                    return False, submatrix
    return True, None


def test_TUM(runs):
    for _ in tqdm(range(runs)):
        generator = SPASTGen(5, 1, 2, 3, 1, 0.5, 0.5)
        generator.generate_instance()
        generator.write_instance_to_file("instance.txt")

        G = GurobiSPAST("instance.txt", output_flag=0)
        G.solve()
        G.display_assignments()

        constr_mat = G.J.getA().toarray()
        bool_TUM, error_mat = is_TUM(constr_mat)
        if not bool_TUM:
            with open("instance.txt", "r") as f:
                print(f.read())
            print(f"\n{error_mat}\n")
            break


if __name__ == "__main__":
    test_TUM(100)
