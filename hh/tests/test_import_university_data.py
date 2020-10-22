from unittest import TestCase

from ruamel.yaml.comments import CommentedMap

from hh.actions.import_university_data import process_university_data, sort_data


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

    def test_sort_data(self):
        """
        Should return a sorted version of the data
        """
        data = {
            "gt": {"uni2": set(["campus2", "campus1"]), "uni1": set(["campus3"])},
            "ec": {"uni3": set(["campus4"])},
        }
        expected = CommentedMap(
            [
                ["ec", CommentedMap([["uni3", ["campus4"]]])],
                [
                    "gt",
                    CommentedMap(
                        [["uni1", ["campus3"]], ["uni2", ["campus1", "campus2"]]]
                    ),
                ],
            ]
        )
        self.assertEqual(sort_data(data), expected)
