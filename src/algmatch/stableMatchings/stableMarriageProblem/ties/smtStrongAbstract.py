"""
Stable Marriage Problem With Ties - Strong-Stability-Specific Abstract Class
Stores Hopcroft-Karp implementation for finding the maximum matching
"""

from collections import deque

from algmatch.stableMatchings.stableMarriageProblem.ties.smtAbstract import SMTAbstract


class SMTStrongAbstract(SMTAbstract):
    def __init__(
        self, filename: str | None = None, dictionary: dict | None = None
    ) -> None:
        super().__init__(
            filename=filename, dictionary=dictionary, stability_type="strong"
        )
        # used to find the critical set and final answer
        self.maximum_matching = {}
        self.dist = {}

    def _reset_maximum_matching(self):
        self.maximum_matching = {
            "men": {m: None for m in self.men},
            "women": {w: None for w in self.women},
        }
        self.dist = {}

    def _BFS(self):
        queue = deque(maxlen=len(self.men))
        self.dist = {None: float("inf")}
        for m in self.men:
            if self.maximum_matching["men"][m] is None:
                self.dist[m] = 0
                queue.append(m)
            else:
                self.dist[m] = float("inf")

        while queue:
            m = queue.popleft()
            if self.dist[m] < self.dist[None]:
                for w in self.M[m]["assigned"]:
                    partner = self.maximum_matching["women"][w]
                    if self.dist[partner] == float("inf"):
                        self.dist[partner] = self.dist[m] + 1
                        queue.append(partner)

        return self.dist[None] != float("inf")

    def _DFS(self, m):
        if m is not None:
            for w in self.M[m]["assigned"]:
                partner = self.maximum_matching["women"][w]
                if self.dist[partner] == self.dist[m] + 1:
                    if self._DFS(partner):
                        self.maximum_matching["women"][w] = m
                        self.maximum_matching["men"][m] = w
                        return True
            self.dist[m] = float("inf")
            return False
        return True

    def _get_maximum_matching(self):
        """
        An implementation of Hopcroft-Karp
        """
        self._reset_maximum_matching()
        while self._BFS():
            for m in self.men:
                if self.maximum_matching["men"][m] is None:
                    self._DFS(m)

    def _select_maximum_matching(self):
        self._get_maximum_matching()
        for m, w in self.maximum_matching["men"].items():
            self.M[m]["assigned"] = w
        for w, m in self.maximum_matching["women"].items():
            self.M[w]["assigned"] = m
