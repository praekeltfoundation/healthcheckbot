from unittest import TestCase

from hh.actions.import_university_data import process_university_data


class TestImportUniversityData(TestCase):
    def test_process_university_data(self):
        """
        Should correctly process the university data
        """
        source = [
            {" Province": "KZN", "TVET ": "Elangeni", "Campus": "Central Office "},
            {
                "Province": "WC",
                "University": "Cape Peninsula University of Technology (CPUT)",
                "Campus": "Cape Town",
            },
            {
                "Province": "Western Cape",
                "PHEI": "Boston City Campus & Business College ",
                "Campus": "Belville",
            },
            {
                "Province": "Western Cape",
                "PHEI": "Boston City Campus & Business College ",
                "Campus": "George",
            },
        ]
        result = process_university_data(source)
        self.assertEqual(
            result,
            {
                "nl": {"Elangeni": {"Central Office"}},
                "wc": {
                    "Cape Peninsula University of Technology (CPUT)": {"Cape Town"},
                    "Boston City Campus & Business College": {"Belville", "George"},
                },
            },
        )
