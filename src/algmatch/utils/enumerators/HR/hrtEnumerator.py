from algmatch.stableMatchings.hospitalResidentsProblem.ties.hrtAbstract import (
    HRTAbstract,
)
from algmatch.utils.enumerators.HR.hrGenericEnumerator import HRGenericEnumerator
from algmatch.abstractClasses.preferenceSource import PreferenceSource
from algmatch.abstractClasses.stabilityType import StabilityType


class HRTEnumerator(HRTAbstract, HRGenericEnumerator):
    def __init__(self, dictionary, stability_type):
        source = PreferenceSource(dictionary=dictionary)
        stability_type = StabilityType.from_value(stability_type)
        HRTAbstract.__init__(self, source=source, stability_type=stability_type)
        HRGenericEnumerator.__init__(self)

    def has_stability(self) -> bool:
        if self.stability_type == StabilityType.SUPER:
            return self._check_super_stability()
        elif self.stability_type == StabilityType.STRONG:
            return self._check_strong_stability()
        else:
            raise ValueError("Stability type is neither 'super' nor 'strong'")

    def resident_trial_order(self, resident):
        for tie in self.residents[resident]["list"]:
            for hospital in tie:
                yield hospital
