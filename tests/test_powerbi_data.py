import csv
import pathlib
import unittest


PROJECT = pathlib.Path(__file__).resolve().parent.parent
PLANNING = "Planning only (not operational)"


def read_rows(path):
    with path.open(newline="", encoding="utf-8") as handle:
        return list(csv.DictReader(handle))


class PowerBiDataTests(unittest.TestCase):
    def setUp(self):
        source_rows = read_rows(PROJECT / "sites.csv")
        bi_rows = read_rows(PROJECT / "powerbi" / "ai_water_sites.csv")
        self.source = {
            (row["operator"], row["location"]): row for row in source_rows
        }
        self.bi = {
            (
                row["Operator"],
                row["City"] + (", " + row["State"] if row["State"] else ""),
            ): row
            for row in bi_rows
        }
        self.assertEqual(len(self.source), len(source_rows))
        self.assertEqual(len(self.bi), len(bi_rows))
        self.assertEqual(self.source.keys(), self.bi.keys())

    def test_planning_filter_excludes_source_planning_rows(self):
        expected = {
            key for key, row in self.source.items()
            if row["motive_tier"] == "planning_not_measured"
        }
        excluded = {
            key for key, row in self.bi.items() if row["Status"] == PLANNING
        }
        self.assertTrue(expected)
        self.assertEqual(excluded, expected)

    def test_non_planning_rows_retain_source_status(self):
        labels = {
            "primary": "Primary-verified",
            "framework_secondary": "Framework secondary",
        }
        expected = {
            key: labels[row["motive_tier"]]
            for key, row in self.source.items()
            if row["motive_tier"] != "planning_not_measured"
        }
        retained = {
            key: row["Status"] for key, row in self.bi.items()
            if row["Status"] != PLANNING
        }
        self.assertTrue(expected)
        self.assertEqual(retained, expected)


if __name__ == "__main__":
    unittest.main()
