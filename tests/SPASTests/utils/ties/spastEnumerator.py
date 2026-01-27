from algmatch.stableMatchings.studentProjectAllocation.ties.spastAbstract import (
    SPASTAbstract,
)
from tests.SPASTests.utils.generic.spasGenericEnumerator import SPASGenericEnumerator


class SPASTEnumerator(SPASTAbstract, SPASGenericEnumerator):
    def __init__(self, dictionary, stability_type):
        SPASTAbstract.__init__(
            self, dictionary=dictionary, stability_type=stability_type
        )
        SPASGenericEnumerator.__init__(self)

    def has_stability(self):
        if self.stability_type == "super":
            return self._check_super_stability()
        elif self.stability_type == "strong":
            return self._check_strong_stability()
        else:
            raise ValueError("Stability type is neither 'super' or 'strong'")

    def student_trial_order(self, student):
        for tie in self.students[student]["list"]:
            for project in tie:
                yield project
