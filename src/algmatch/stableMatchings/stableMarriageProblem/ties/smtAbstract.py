"""
Stable Marriage Problem With Ties - Abstract class
"""

from copy import deepcopy
import os

from algmatch.stableMatchings.stableMarriageProblem.ties.smtPreferenceInstance import (
    SMTPreferenceInstance,
)


class SMTAbstract:
    def __init__(
        self,
        filename: str | None = None,
        dictionary: dict | None = None,
        stability_type: str = None,
    ) -> None:
        assert filename is not None or dictionary is not None, (
            "Either filename or dictionary must be provided"
        )
        assert not (filename is not None and dictionary is not None), (
            "Only one of filename or dictionary must be provided"
        )

        self._assert_valid_stability_type(stability_type)
        self.stability_type = stability_type.lower()

        if filename is not None:
            assert os.path.isfile(filename), f"File {filename} does not exist"
            self._reader = SMTPreferenceInstance(filename=filename)

        if dictionary is not None:
            self._reader = SMTPreferenceInstance(dictionary=dictionary)

        self.men = self._reader.men
        self.women = self._reader.women

        self.original_men = deepcopy(self.men)
        self.original_women = deepcopy(self.women)

        self.M = {}  # provisional matching
        self.stable_matching = {
            "man_sided": {m: "" for m in self.men},
            "woman_sided": {w: "" for w in self.women},
        }
        self.is_stable = False

    @staticmethod
    def _assert_valid_stability_type(st) -> None:
        assert st is not None, "Select a stability type - either 'super' or 'strong'"
        assert type(st) is str, "Stability type is not str'"
        assert st.lower() in ("super", "strong"), (
            "Stability type must be either 'super' or 'strong'"
        )

    def _check_super_stability(self) -> bool:
        # first check for multiple-assignment
        seen_matching_targets = set()
        for person in self.M:
            matching_target = self.M[person]["assigned"]
            if matching_target in seen_matching_targets:
                return False
            if matching_target is not None:
                seen_matching_targets.add(matching_target)

        # stability must be checked with regards to the original lists prior to deletions
        for man, m_prefs in self.original_men.items():
            preferred_women = self.original_men[man]["list"]
            matched_woman = self.M[man]["assigned"]

            if matched_woman is not None:
                rank_matched_woman = m_prefs["rank"][matched_woman]
                # every woman that m_i prefers to his matched partner or is indifferent between them
                preferred_women = m_prefs["list"][: rank_matched_woman + 1]

            for w_tie in preferred_women:
                for woman in w_tie:
                    if woman == matched_woman:
                        continue

                    existing_fiance = self.M[woman]["assigned"]
                    if existing_fiance is None:
                        return False
                    else:
                        w_prefs = self.original_women[woman]
                        rank_fiance = w_prefs["rank"][existing_fiance]
                        rank_man = w_prefs["rank"][man]
                        if rank_man <= rank_fiance:
                            return False
        return True

    def _check_strong_stability(self) -> bool:
        # first check for multiple-assignment
        seen_matching_targets = set()
        for person in self.M:
            matching_target = self.M[person]["assigned"]
            if matching_target in seen_matching_targets:
                return False
            if matching_target is not None:
                seen_matching_targets.add(matching_target)

        # stability must be checked with regards to the original lists prior to deletions
        for man, m_prefs in self.original_men.items():
            matched_woman = self.M[man]["assigned"]

            if matched_woman is not None:
                rank_matched_woman = m_prefs["rank"][matched_woman]
                preferred_women = m_prefs["list"][:rank_matched_woman]
                indifferent_women = m_prefs["list"][rank_matched_woman]
            else:
                preferred_women = self.original_men[man]["list"]
                indifferent_women = []

            for w_tie in preferred_women:
                for woman in w_tie:
                    existing_fiance = self.M[woman]["assigned"]
                    if existing_fiance is None:
                        return False
                    else:
                        w_prefs = self.original_women[woman]
                        rank_fiance = w_prefs["rank"][existing_fiance]
                        rank_man = w_prefs["rank"][man]
                        if rank_man <= rank_fiance:
                            return False

            for woman in indifferent_women:
                existing_fiance = self.M[woman]["assigned"]
                if existing_fiance is None:
                    return False
                else:
                    w_prefs = self.original_women[woman]
                    rank_fiance = w_prefs["rank"][existing_fiance]
                    rank_man = w_prefs["rank"][man]
                    if rank_man < rank_fiance:
                        return False

        return True

    def _get_pref_list(self, person) -> list:
        if person in self.men:
            return self.men[person]["list"]
        elif person in self.women:
            return self.women[person]["list"]
        else:
            raise ValueError(f"{person} is not a man or a woman")

    def _get_pref_ranks(self, person) -> dict:
        if person in self.men:
            return self.men[person]["rank"]
        elif person in self.women:
            return self.women[person]["rank"]
        else:
            raise ValueError(f"{person} is not a man or a woman")

    def _get_pref_length(self, person) -> int:
        pref_list = self._get_pref_list(person)
        total = sum([len(tie) for tie in pref_list])
        return total

    def _get_head(self, person) -> set:
        pref_list = self._get_pref_list(person)
        idx = 0
        while idx < len(pref_list):
            head = pref_list[idx]
            if len(head) > 0:
                return head
            idx += 1
        raise ValueError("Pref_list empty")

    def _get_tail(self, person) -> set:
        pref_list = self._get_pref_list(person)
        idx = len(pref_list) - 1
        while idx >= 0:
            tail = pref_list[idx]
            if len(tail) > 0:
                return tail
            idx -= 1
        raise ValueError("Pref_list empty")

    def _engage(self, man, woman) -> None:
        self.M[man]["assigned"].add(woman)
        self.M[woman]["assigned"].add(man)

    def _break_engagement(self, man, woman) -> None:
        self.M[man]["assigned"].discard(woman)
        self.M[woman]["assigned"].discard(man)

    def _delete_pair(self, man, woman) -> None:
        if man in self.women:
            man, woman = woman, man
        for tie in self.men[man]["list"]:
            tie.discard(woman)
        for tie in self.women[woman]["list"]:
            tie.discard(man)

    def _delete_tail(self, person) -> None:
        tail = self._get_tail(person)
        while len(tail) != 0:
            deletion = tail.pop()
            self._delete_pair(person, deletion)

    def _break_all_engagements(self, person) -> None:
        assignee_set = self.M[person]["assigned"]
        while len(assignee_set) != 0:
            assignee = assignee_set.pop()
            self._break_engagement(person, assignee)

    def _reject_lower_ranks(self, target, proposer) -> None:
        rank_p = self._get_pref_ranks(target)[proposer]
        for reject_tie in self._get_pref_list(target)[rank_p + 1 :]:
            while len(reject_tie) != 0:
                reject = reject_tie.pop()
                self._break_engagement(target, reject)
                self._delete_pair(target, reject)

    def _neighbourhood(self, people):
        if not people:
            return set()
        return set.union(*[self.M[person]["assigned"] for person in people])

    def _while_loop(self) -> bool:
        raise NotImplementedError("Method _while_loop must be implemented in subclass")

    def save_man_sided(self) -> None:
        for man in self.men:
            woman = self.M[man]["assigned"]
            if woman is not None:
                self.stable_matching["man_sided"][man] = woman

    def save_woman_sided(self) -> None:
        for woman in self.women:
            man = self.M[woman]["assigned"]
            if man is not None:
                self.stable_matching["woman_sided"][woman] = man

    def run(self) -> None:
        if self._while_loop():
            self.save_man_sided()
            self.save_woman_sided()

            if self.stability_type == "super":
                self.is_stable = self._check_super_stability()
            else:
                self.is_stable = self._check_strong_stability()

            if self.is_stable:
                return f"super-stable matching: {self.stable_matching}"
        return "no super-stable matching"
