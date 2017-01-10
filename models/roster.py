import csv


class Roster(object):
    def __init__(self, filename, delimiter="\t"):
        with open(filename) as f:
            lines = []
            dicts = csv.DictReader(f, delimiter=delimiter)
            for item in dicts:
                lines.append(item)
            self.data = lines

    def search(self, searchKey, searchValue):
        """Returns dictionaries in the roster with element matching search key/value, else none"""
        dicts = [item for item in self.data if item[searchKey] == searchValue]
        if len(dicts) < 1:
            return None
        else:
            return dicts
