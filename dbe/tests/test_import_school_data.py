import tempfile

from dbe.actions.import_school_data import read_file


class TestImportSchoolData:
    def test_read_file(self):
        """
        Should return the relevant school data from the CSV
        """
        (_, filename) = tempfile.mkstemp()
        with open(filename, "w") as f:
            f.write(
                "Unrelated,NatEMIS,Province,Official_Institution_Name\n"
                "1,123456,KZN,school 1\n"
                "2,654321,MP,school 2\n"
            )
        schools = read_file(filename)
        assert schools == set(
            (("123456", "nl", "school 1"), ("654321", "mp", "school 2"))
        )
