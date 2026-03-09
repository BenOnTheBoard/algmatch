from algmatch.utils.enumerators.HR.hrGenericBruteForcer import HRGenericBruteForcer


class HRGenericEnumerator(HRGenericBruteForcer):
    def __init__(self):
        HRGenericBruteForcer.__init__(self)

    def add_pair(self, resident, hospital) -> None:
        HRGenericBruteForcer.add_pair(self, resident, hospital)
        if self.hospital_is_full(hospital):
            self.full_hospitals.add(hospital)

    def delete_pair(self, resident, hospital) -> None:
        HRGenericBruteForcer.delete_pair(self, resident, hospital)
        self.full_hospitals.discard(hospital)

    def choose(self, i=1) -> None:
        # if every resident is assigned
        if i > len(self.residents):
            if self.has_stability():
                self.save_matching()

        else:
            resident = "r" + str(i)
            for hospital in self.resident_trial_order(resident):
                if hospital not in self.full_hospitals:
                    self.add_pair(resident, hospital)

                    self.choose(i + 1)

                    self.delete_pair(resident, hospital)
            # case where the resident is unassigned
            self.choose(i + 1)

    # alias with more readable name
    def find_stable_matchings(self) -> None:
        self.choose()
