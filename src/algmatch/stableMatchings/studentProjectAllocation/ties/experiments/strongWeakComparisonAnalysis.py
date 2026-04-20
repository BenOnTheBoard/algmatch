import json
import os


"""
Abstract function to find matchings based on a condition.

:param: condition: function that takes a time object and returns True if a matching is found
:return: function that takes a results directory and write file path and writes matching data to the write file
based on the given condition
"""
def find_matchings_abstract(condition):
    def _curried(results_dir, write_file):
        found = 0
        with open(write_file, 'w') as write_to:
            for file in os.listdir(results_dir):
                with open(os.path.join(results_dir, file)) as f:
                    data = json.load(f)
                    for i, time in enumerate(data['times']):
                        if condition(time):
                            found += 1
                            print(f"{file.split('.')[0]}_instance_{i}.txt", file=write_to)

        print(f"Found {found} matching instances, stored in {write_file}.")

    return _curried


"""
Function to grab results where strong matching exists
and is different to weak matching.
"""
find_differing_matchings = find_matchings_abstract(
    lambda time: any(time['strong']['rank']) and time['weak']['rank'] != time['strong']['rank']
)


"""
Function to grab results where strong matching exists
and has different size to weak matching.
"""
find_different_size_matchings = find_matchings_abstract(
    lambda time: any(time['strong']['rank']) and
        sum(time['strong']['rank']) != sum(time['weak']['rank'])
)


if __name__ == "__main__":
    RESULTS_DIR = os.getenv("RESULTS_DIR", "./")

    find_differing_matchings(RESULTS_DIR, "differing_matchings.txt")
    find_different_size_matchings(RESULTS_DIR, "different_size_matchings.txt")
