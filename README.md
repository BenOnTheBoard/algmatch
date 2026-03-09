[![DOI](https://zenodo.org/badge/854564426.svg)](https://doi.org/10.5281/zenodo.17752189)

# Algmatch

Algmatch contains implementations of polynomial-time algorithms for matching problems. The full list of support problem is as follow:
- SM: Stable Marriage
- HR: Hospital/Residents
    - Resident-optimal algorithm and hospital-optimal algorithm
- SPA-S: Student Project Allocation with lecturer preferences over students
    - Student-optimal algorithm and lecturer-optimal algorithm
- SPA-P: Student Project Allocation with lecturer preferences over projects (requires Gurobi)
    - for usage, see [this](https://github.com/BenOnTheBoard/algmatch/blob/main/SPAP_Usage.ipynb) notebook.
- SR: Stable Roommates
- SMT: Strong and Super-stable matchings in Stable Marriage with Ties
- HRT: Hospital/Residents with Ties
    - Strong: Resident-optimal algorithm and hospital-optimal algorithm for strong stability
    - Super: Resident-optimal algorithm and hospital-optimal algorithm for super-stability
- SPA-ST: Student Project Allocation with lecturer preferences over students and ties
    - Super: Student-optimal algorithm
    - There are no published lecturer-optimal algorithm for super-stability or any published algorithm for strong stability exists at this time.

Requires Python 3.10 or later.

Format data according to the guidelines in [this](https://github.com/BenOnTheBoard/algmatch/tree/v1.0.1/DATA_FORMAT_GUIDELINES) folder.

# Installation

Simply run `pip install algmatch`.

# Usage

To import a specific algorithm, use `from algmatch import <algorithm>`, e.g. `from algmatch import SPAS` or `from algmatch import StudentProjectAllocation`.
Create a file or dictionary with your instance, following the guidelines in the [`DATA_FORMAT_GUIDELINES`](https://github.com/BenOnTheBoard/algmatch/tree/v1.0.1/DATA_FORMAT_GUIDELINES) folder.
For example, 

Importing data:

```python
from algmatch import HR, SM, SPAS

spas_instance = {
    'students': {
        1: [1, 2],
        2: [2, 3],
        3: [3, 1],
        4: [4, 1]
    },
    'projects': {
        1: {
            'capacity': 1,
            'lecturer': 1
        },
        2: {
            'capacity': 1,
            'lecturer': 1
        },
        3: {
            'capacity': 1,
            'lecturer': 2
        },
        4: {
            'capacity': 1,
            'lecturer': 2
        }
    },
    'lecturers': {
        1: {
            'capacity': 2,
            'preferences': [3, 1, 2, 4]
        },
        2: {
            'capacity': 2,
            'preferences': [2, 4, 3]
        }
    }
}

spas_student = SPAS(dictionary=spas_instance, optimised_side="students")
spas_lecturer = SPAS(dictionary=spas_instance, optimised_side="lecturers")
```

Getting the stable matchings:

```python
spas_2_student_stable_matching = spas_2_student.get_stable_matching()
spas_2_lecturer_stable_matching = spas_2_lecturer.get_stable_matching()

print("SPA 2 student stable matching:"
print(spas_2_student_stable_matching)

print("SPA 2 lecturer stable matching:")
print(spas_2_lecturer_stable_matching)
```

```
SPA student stable matching:
{'student_sided': {'s1': 'p1', 's2': 'p2', 's3': 'p3', 's4': 'p4'}, 'lecturer_sided': {'l1': ['s1', 's2'], 'l2': ['s3', 's4']}}
SPA lecturer stable matching:
{'student_sided': {'s1': 'p2', 's2': 'p3', 's3': 'p1', 's4': 'p4'}, 'lecturer_sided': {'l1': ['s1', 's3'], 'l2': ['s2', 's4']}}
```

See more example usage [here](https://github.com/BenOnTheBoard/algmatch/blob/v1.0.1/examples.ipynb).

# Further details

- All algorithms implemented (barring SPA-P) have verification testing
  - Tested by producing random instances
  - Brute force all stable matchings
  - Check algorithm is generating correct stable matchings
