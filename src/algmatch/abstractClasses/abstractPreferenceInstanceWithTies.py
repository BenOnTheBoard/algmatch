"""
Abstract class to store preference lists for both sides in matching problems that have ties in the preference lists.
"""

from algmatch.abstractClasses.abstractPreferenceInstance import (
    AbstractPreferenceInstance,
)

from algmatch.errors.InstanceSetupErrors import PrefRepError, PrefNotFoundError


class AbstractPreferenceInstanceWithTies(AbstractPreferenceInstance):
    def __init__(
        self, filename: str | None = None, dictionary: dict | None = None
    ) -> None:
        super().__init__(filename, dictionary)

    def any_repetitions(self, prefs):
        seen_count = 0
        seen_set = set()
        for tie in prefs:
            seen_count += len(tie)
            seen_set |= tie
        if len(seen_set) != seen_count:
            return True
        return False

    def tied_lists_to_rank(self, group) -> None:
        """
        Utility. Takes a group with clean lists and constructs their rank dictionaries.

        :param group: set of entities (e.g. men, projects, lecturers)
        """
        for prefs in group.values():
            prefs["rank"] = dict()
            for idx, target_set in enumerate(prefs["list"]):
                prefs["rank"] |= {target: idx for target in target_set}

    def check_preferences_with_ties_single_group(
        self, group, name_singular, targets
    ) -> None:
        """
        Utility. Checks that each list contains only valid targets without repetition.

        :param group:  set of entities (e.g. men, projects, lecturers)
        :param name_singular: singular of group name
        :param targets: group of valid targets of preference
        :raises PrefRepError: target duplication
        :raises PrefNotFoundError: target is not is not of the right kind
        """
        for g, prefs in group.items():
            if self.any_repetitions(prefs["list"]):
                raise PrefRepError(name_singular, g)

            for tie in prefs["list"]:
                for t in tie:
                    if t not in targets:
                        raise PrefNotFoundError(name_singular, g, t)
