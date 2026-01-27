"""
Class to read in a file of preferences for the SPA-ST problem.
Specifically in a format convenient for the IP model solver.
"""

from algmatch.abstractClasses.abstractReader import AbstractReader
from algmatch.stableMatchings.studentProjectAllocation.ties.entityPreferenceInstance import EntityPreferenceInstance as EPI
from algmatch.stableMatchings.studentProjectAllocation.ties.fileReader import FileReader

from pprint import pprint


class FileReaderIPModel(AbstractReader):
    def __init__(self, filename: str) -> None:
        super().__init__(filename)
        
        if filename.endswith('.txt'): self.delim = ' '
        elif filename.endswith('.csv'): self.delim = ','

        self.students = {} # student -> [project preferences, {project: assigned?}]
        self.projects = {} # project -> [capacity, lecturer]
        self.lecturers = {} # lecturer -> [capacity, preferences]

        self._file_reader = FileReader(filename)
        self._read_data()

    
    def _read_data(self):
        for student in self._file_reader.students:
            project_data = self._file_reader.students[student]
            self.students[student] = [
                project_data["list"],
                {EPI(p): 0 for project in project_data["list"] for p in project}
            ]

        for project in self._file_reader.projects:
            project_data = self._file_reader.projects[project]
            self.projects[project] = [
                project_data["upper_quota"],
                project_data["lecturer"],
            ]

        for lecturer in self._file_reader.lecturers:
            lecturer_data = self._file_reader.lecturers[lecturer]
            self.lecturers[lecturer] = [
                lecturer_data["upper_quota"],
                lecturer_data["list"],
            ]


if __name__ == '__main__':
    fr = FileReaderIPModel('instance.txt')
    pprint(fr.students)
    pprint(fr.projects)
    pprint(fr.lecturers)