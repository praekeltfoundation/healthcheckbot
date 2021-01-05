import tempfile

from dbe.actions.import_marking_centres import read_file


class TestImportMarkingCentres:
    def test_read_file(self):
        """
        Should return the relevant marking centre data from the CSV
        """
        (_, filename) = tempfile.mkstemp()
        with open(filename, "w") as f:
            f.write("PROVINCE,NAME\n" "nl,school 1\n" "mp,school 2\n")
        centres = read_file(filename)
        assert centres == set((("nl", "school 1"), ("mp", "school 2")))
