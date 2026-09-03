"""
Class to read in file for a SPA-P instance.
"""

from algmatch.abstractClasses.abstractReader import AbstractReader


class FileReader(AbstractReader):
    def __init__(self, filename: str, is_instance: bool = True) -> None:
        super().__init__(filename)

        if filename.endswith(".txt"):
            self.delim = " "
        elif filename.endswith(".csv"):
            self.delim = ","

        if is_instance:
            self.students = {}  # student -> [project preferences, {project: assigned?}]
            self.projects = {}  # project -> [capacity, lecturer, num students assigned]
            self.lecturers = {}  # lecturer -> [capacity, project preferences, num students assigned, worst project]

            self._read_data()

        else:
            self.solution = self._read_solution(filename)

    def _read_data(self) -> None:
        with open(self.data, "r") as f:
            f = f.readlines()
            student_size, project_size, _ = map(int, f[0].strip().split(self.delim))

            for L in f[1 : student_size + 1]:
                line = L.strip().split(self.delim)
                self.students[f"s{line[0]}"] = [
                    [f"p{i}" for i in line[1:]],
                    {f"p{i}": 0 for i in line[1:]},
                ]

            for L in f[student_size + 1 : student_size + project_size + 1]:
                line = L.strip().split(self.delim)
                self.projects[f"p{line[0]}"] = [int(line[1]), f"l{line[2]}", 0]

            for L in f[student_size + project_size + 1 :]:
                line = L.strip().split(self.delim)
                self.lecturers[f"l{line[0]}"] = [
                    int(line[1]),
                    [f"p{i}" for i in line[2:]],
                    0,
                    None,
                ]

    def _read_solution(self, filename: str) -> dict[str, str]:
        """
        Read solution in either txt or csv format.
        Return dictionary mapping students to assigned projects.
        """
        if filename.endswith(".csv"):
            delim = ","
        elif filename.endswith(".txt"):
            delim = " "

        with open(filename, "r") as f:
            f = f.readlines()
            return {
                f"s{line[0]}": f"p{line[1]}" if line[1] else ""
                for line in [L.strip().split(delim) for L in f]
            }
