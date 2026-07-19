from algmatch.stableMatchings.studentProjectAllocation.ties.spastAbstract import (
    SPASTAbstract,
)
from algmatch.utils.enumerators.SPAS.spasGenericEnumerator import SPASGenericEnumerator
from algmatch.abstractClasses.stabilityType import StabilityType


class SPASTEnumerator(SPASTAbstract, SPASGenericEnumerator):
    def __init__(self, dictionary, stability_type):
        stability_type = StabilityType.from_value(stability_type)
        SPASTAbstract.__init__(
            self, dictionary=dictionary, stability_type=stability_type
        )
        SPASGenericEnumerator.__init__(self)

    def has_stability(self):
        if self.stability_type == StabilityType.SUPER:
            return self._check_super_stability()
        elif self.stability_type == StabilityType.STRONG:
            return self._check_strong_stability()
        else:
            raise ValueError("Stability type is neither 'super' nor 'strong'")

    def student_trial_order(self, student):
        for tie in self.students[student]["list"]:
            for project in tie:
                yield project
