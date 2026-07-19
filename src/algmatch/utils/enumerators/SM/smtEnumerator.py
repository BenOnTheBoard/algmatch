from algmatch.stableMatchings.stableMarriageProblem.ties.smtAbstract import SMTAbstract
from algmatch.utils.enumerators.SM.smGenericEnumerator import SMGenericEnumerator
from algmatch.abstractClasses.stabilityType import StabilityType


class SMTEnumerator(SMTAbstract, SMGenericEnumerator):
    def __init__(self, dictionary, stability_type):
        stability_type = StabilityType.from_value(stability_type)
        SMTAbstract.__init__(self, dictionary=dictionary, stability_type=stability_type)
        SMGenericEnumerator.__init__(self)

    def has_stability(self) -> bool:
        if self.stability_type == StabilityType.SUPER:
            return self._check_super_stability()
        elif self.stability_type == StabilityType.STRONG:
            return self._check_strong_stability()
        else:
            raise ValueError("Stability type is neither 'super' nor 'strong'")

    def man_trial_order(self, man):
        for tie in self.men[man]["list"]:
            for woman in tie:
                yield woman
