from algmatch.stableMatchings.stableMarriageProblem.noTies.smAbstract import SMAbstract
from tests.SMTests.utils.smGenericEnumerator import SMGenericEnumerator


class SMEnumerator(SMAbstract, SMGenericEnumerator):
    def __init__(self, dictionary):
        SMAbstract.__init__(self, dictionary=dictionary)
        SMGenericEnumerator.__init__(self)

    def has_stability(self) -> bool:
        return self._check_stability()

    def man_trial_order(self, man):
        for woman in self.men[man]["list"]:
            yield woman
