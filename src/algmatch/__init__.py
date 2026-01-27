# === Non-bipartite ===
from .stableRoommatesProblem import StableRoommatesProblem
from .stableRoommatesProblem import StableRoommatesProblem as SR

# === Bipartite ===

# --- No Ties ---
from .stableMarriageProblem import StableMarriageProblem
from .stableMarriageProblem import StableMarriageProblem as SM

from .hospitalResidentsProblem import HospitalResidentsProblem
from .hospitalResidentsProblem import HospitalResidentsProblem as HR

from .studentProjectAllocation import StudentProjectAllocation
from .studentProjectAllocation import StudentProjectAllocation as SPAS

# --- Ties ---
from .stableMarriageProblemWithTies import StableMarriageProblemWithTies
from .stableMarriageProblemWithTies import StableMarriageProblemWithTies as SMT

from .hospitalResidentsProblemWithTies import HospitalResidentsProblemWithTies
from .hospitalResidentsProblemWithTies import HospitalResidentsProblemWithTies as HRT

# === SPA-P ===

from .studentProjectAllocationProjects import StudentProjectAllocationProjectsSingle
from .studentProjectAllocationProjects import StudentProjectAllocationProjectsMultiple

from .studentProjectAllocationProjects import (
    StudentProjectAllocationProjectsSingle as SPAP_Single,
)
from .studentProjectAllocationProjects import (
    StudentProjectAllocationProjectsMultiple as SPAP_Multiple,
)
from .stableMatchings.studentProjectAllocation.SPA_P import utils as SPAP_utils

from .stableMatchings.studentProjectAllocation.SPA_P import (
    instanceGenerators as SPAP_instanceGenerators,
)
from .stableMatchings.studentProjectAllocation.SPA_P import instanceGenerators as SPAPIG
