"""
Class to provide interface for the Stable Marriage Problem algorithm that contains the following extensions:
- both man and woman optimal solutions
- methods for getting the MGS-, WGS- and GS-lists
"""

import os

from stableMatchings.stableMarriageProblem.smManOptimal import SMManOptimal
from stableMatchings.stableMarriageProblem.smWomanOptimal import SMWomanOptimal

class StableMarriageGSLists:
    def __init__(self, filename: str | None = None, dictionary: dict | None = None) -> None:
        """
        Initialise the Stable Marriage Problem algorithm.

        :param filename: str, optional, default=None, the path to the file to read in the preferences from.
        :param dictionary: dict, optional, default=None, the dictionary of preferences.
        """
        if filename is not None:
            filename = os.path.join(os.path.dirname(__file__), filename)

        self.man_oriented_sm = SMManOptimal(filename=filename, dictionary=dictionary)
        self.woman_oriented_sm = SMWomanOptimal(filename=filename, dictionary=dictionary)

        self.man_oriented_sm.run()
        self.woman_oriented_sm.run()

        self.MGS_lists = {k: v["list"] for k,v in (self.man_oriented_sm.men | self.man_oriented_sm.women).items()}
        self.WGS_lists = {k: v["list"] for k,v in (self.woman_oriented_sm.men | self.woman_oriented_sm.women).items()}
       
        self.GS_lists = {}
       
        for k,v in self.MGS_lists.items():
            self.GS_lists[k] = []
            for w in v:
                if w in self.WGS_lists[k]:
                    self.GS_lists[k].append(w)


    def get_M_0(self) -> dict:
        """
        :return: dict, the man-optimal stable matching.
        """
        return self.man_oriented_sm.stable_matching
    
    def get_M_z(self) -> dict:
        """
        :return: dict, the woman-optimal stable matching.
        """
        return self.woman_oriented_sm.stable_matching
    
    def get_MGS_Lists(self) -> dict:
        """
        :return: dict, the undeleted preferences from the man-oriented execution
        """
        return self.MGS_lists
    
    def get_WGS_Lists(self) -> dict:
        """
        :return: dict, the undeleted preferences from the woman-oriented execution
        """
        return self.WGS_lists
    
    def get_GS_Lists(self) -> dict:
        """
        :return: dict, the intersection of the MGS- and WGS-lists
        """
        return self.GS_lists