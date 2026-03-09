from algmatch.stableMatchings.stableMarriageProblem.ties.smtAbstract import SMTAbstract
from tests.SMTests.utils.smGenericEnumerator import SMGenericEnumerator


class SMTEnumerator(SMTAbstract, SMGenericEnumerator):
    def __init__(self, dictionary, stability_type):
        SMTAbstract.__init__(self, dictionary=dictionary, stability_type=stability_type)
        SMGenericEnumerator.__init__(self)

    def has_stability(self) -> bool:
        if self.stability_type == "super":
            return self._check_super_stability()
        elif self.stability_type == "strong":
            return self._check_strong_stability()
        else:
            raise ValueError("Stability type is neither 'super' or 'strong'")

    def man_trial_order(self, man):
        for tie in self.men[man]["list"]:
            for woman in tie:
                yield woman
