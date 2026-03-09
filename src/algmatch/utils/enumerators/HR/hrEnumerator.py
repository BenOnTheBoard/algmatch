from algmatch.stableMatchings.hospitalResidentsProblem.noTies.hrAbstract import (
    HRAbstract,
)
from algmatch.utils.enumerators.HR.hrGenericEnumerator import HRGenericEnumerator


class HREnumerator(HRAbstract, HRGenericEnumerator):
    def __init__(self, dictionary):
        HRAbstract.__init__(self, dictionary=dictionary)
        HRGenericEnumerator.__init__(self)

    def has_stability(self) -> bool:
        return self._check_stability()

    def resident_trial_order(self, resident):
        for hospital in self.residents[resident]["list"]:
            yield hospital
