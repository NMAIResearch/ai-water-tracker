import json
import pathlib
import re
import tempfile
import unittest
from html.parser import HTMLParser

import build_tool


HERE = pathlib.Path(__file__).resolve().parent
FIXTURES = HERE / "fixtures"
PROJECT = HERE.parent


class IdCollector(HTMLParser):
    def __init__(self):
        super().__init__()
        self.ids = []

    def handle_starttag(self, tag, attrs):
        del tag
        for key, value in attrs:
            if key == "id":
                self.ids.append(value)


class BuildToolTests(unittest.TestCase):
    def fixture_data(self):
        sites = build_tool.read_csv(FIXTURES / "sites.csv")
        sources = build_tool.read_csv(FIXTURES / "water_source_evidence.csv")
        return build_tool.build_site_data(sites, sources)

    def test_fixture_calculations_and_statuses(self):
        data = self.fixture_data()
        self.assertEqual(len(data), 2)
        measured, planning = data
        self.assertAlmostEqual(measured["fy2024"]["consumed"], 5.0)
        self.assertAlmostEqual(measured["fy2024"]["wci"], 0.5)
        self.assertAlmostEqual(measured["fy2025"]["wci"], 0.72)
        self.assertTrue(measured["hydro_coupled"])
        self.assertEqual(measured["water_source"]["potable_2024_Mgal"], 20.0)
        self.assertEqual(planning["status"], "planning_not_measured")
        self.assertEqual(planning["water_source"]["source_class"], "unknown")
        self.assertIsNone(planning["fy2025"]["wci"])

    def test_unknown_evidence_key_is_rejected(self):
        sites = build_tool.read_csv(FIXTURES / "sites.csv")
        sources = build_tool.read_csv(FIXTURES / "water_source_evidence.csv")
        sources[0]["location"] = "Absent Site, ZZ"
        with self.assertRaisesRegex(ValueError, "no matching seed row"):
            build_tool.build_site_data(sites, sources)

    def test_incomplete_source_split_is_rejected(self):
        sites = build_tool.read_csv(FIXTURES / "sites.csv")
        sources = build_tool.read_csv(FIXTURES / "water_source_evidence.csv")
        sources[0]["potable_2024_Mgal"] = ""
        with self.assertRaisesRegex(ValueError, "incomplete 2024 source split"):
            build_tool.build_site_data(sites, sources)

    def test_data_embedding_is_idempotent(self):
        data = self.fixture_data()
        template = (
            "<script>\n/* DATA-START */\nconst DATA = [];\n"
            "/* DATA-END */\n</script>\n"
        )
        rendered = build_tool.render_html(template, data)
        self.assertEqual(build_tool.render_html(rendered, data), rendered)
        match = re.search(
            r"/\* DATA-START \*/\nconst DATA = (.*);\n/\* DATA-END \*/",
            rendered,
            re.DOTALL,
        )
        self.assertIsNotNone(match)
        self.assertEqual(len(json.loads(match.group(1))), 2)

    def test_check_mode_detects_stale_and_current_blocks(self):
        with tempfile.TemporaryDirectory() as directory:
            html = pathlib.Path(directory) / "index.html"
            html.write_text(
                "<script>\n/* DATA-START */\nconst DATA = [];\n"
                "/* DATA-END */\n</script>\n",
                encoding="utf-8",
            )
            args = (
                FIXTURES / "sites.csv",
                FIXTURES / "water_source_evidence.csv",
                html,
            )
            self.assertEqual(build_tool.run(*args, check=True), 1)
            self.assertEqual(build_tool.run(*args, check=False), 0)
            self.assertEqual(build_tool.run(*args, check=True), 0)

    def test_generated_page_has_unique_ids_and_ten_rows(self):
        html = (PROJECT / "index.html").read_text(encoding="utf-8")
        parser = IdCollector()
        parser.feed(html)
        self.assertEqual(len(parser.ids), len(set(parser.ids)))
        match = re.search(
            r"/\* DATA-START \*/\nconst DATA = (.*);\n/\* DATA-END \*/",
            html,
            re.DOTALL,
        )
        self.assertIsNotNone(match)
        data = json.loads(match.group(1))
        self.assertEqual(len(data), 10)
        counts = {
            status: sum(row["status"] == status for row in data)
            for status in ("primary", "planning_not_measured", "framework_secondary")
        }
        self.assertEqual(
            counts,
            {"primary": 6, "planning_not_measured": 3, "framework_secondary": 1},
        )
        documented = [
            row for row in data if row["water_source"]["source_class"] != "unknown"
        ]
        self.assertEqual(len(documented), 3)
        self.assertNotIn("context_cases", html)
        self.assertNotIn("Imperial Valley Computer Manufacturing", html)


if __name__ == "__main__":
    unittest.main()
