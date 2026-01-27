from algmatch.stableMatchings.studentProjectAllocation.noTies.spaAbstract import (
    SPAAbstract,
)
from tests.SPASTests.utils.generic.spasGenericEnumerator import SPASGenericEnumerator


class SPASEnumerator(SPAAbstract, SPASGenericEnumerator):
    def __init__(self, dictionary):
        SPAAbstract.__init__(self, dictionary=dictionary)
        SPASGenericEnumerator.__init__(self)

    def has_stability(self):
        return self._check_stability()

    def student_trial_order(self, student):
        for project in self.students[student]["list"]:
            yield project
