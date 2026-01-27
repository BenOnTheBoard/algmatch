class HRGenericBruteForcer:
    def __init__(self):
        self.M = {r: {"assigned": None} for r in self.residents} | {
            h: {"assigned": set()} for h in self.hospitals
        }
        self.full_hospitals = set()
        self.stable_matching_list = []

        # This lets us order residents in the stable matching by number.
        # We cannot use 'sorted' without this key because that uses lexial order.
        self.resident_order_comparator = lambda r: int(r[1:])

    def hospital_is_full(self, h):
        return self.hospitals[h]["capacity"] == len(self.M[h]["assigned"])

    def add_pair(self, resident, hospital):
        self.M[resident]["assigned"] = hospital
        self.M[hospital]["assigned"].add(resident)

    def delete_pair(self, resident, hospital):
        self.M[resident]["assigned"] = None
        self.M[hospital]["assigned"].remove(resident)

    def save_matching(self):
        stable_matching = {"resident_sided": {}, "hospital_sided": {}}

        for resident in self.residents:
            assigned_hospital = self.M[resident]["assigned"]
            if assigned_hospital is None:
                stable_matching["resident_sided"][resident] = ""
            else:
                stable_matching["resident_sided"][resident] = assigned_hospital

        for hospital in self.hospitals:
            stable_matching["hospital_sided"][hospital] = self.M[hospital][
                "assigned"
            ].copy()
        self.stable_matching_list.append(stable_matching)

    def has_stability(self) -> bool:
        # Link to problem description
        raise NotImplementedError("Enumerators need to link to a stability definition.")

    def resident_trial_order(self, resident) -> str:
        # generator for an order of residentsin preference list
        raise NotImplementedError("Enumerators need to describe the order of matching.")

    def hospital_trial_order(self, hospital) -> str:
        # generator for an order of hospitals in preference list
        raise NotImplementedError("Enumerators need to describe the order of matching.")
