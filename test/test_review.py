import unittest

from fixture import Fixture
from series.acceptance import Acceptance
from series.finding import Finding
from series.impact import Impact
from series.pack import Pack
from series.record import Record

RULE = "A key written twice keeps the first spelling of `setting` it was given.\n"


class ReviewTests(unittest.TestCase):
    # MARK: - Lifecycle
    def setUp(self):
        self.fixture = Fixture()
        self.fixture.spec("APP-1", "accepted", body=RULE)
        self.fixture.spec("APP-2", "accepted", body="Keys: [the rule](../APP-1/SPEC.md#rules).\n")
        self.fixture.spec("APP-3", "accepted", body="Here a key written twice keeps the first spelling.\n")
        self.fixture.spec("APP-4", "draft", supersedes="APP-1", body="A key written twice takes the last `setting`.\n")

    def tearDown(self):
        self.fixture.close()

    # MARK: - Test
    def test_lint_as_accepted_names_each_link_left_on_the_superseded(self):
        # Given
        specification = self.fixture.specification()

        # When
        sut = self.fixture.messages(accepting="APP-4")

        # Then
        self.assertEqual([spec.key for spec in specification.live()], ["APP-1", "APP-2", "APP-3"])
        self.assertEqual(sut, ["spec/APP-2/SPEC.md:11: `../APP-1/SPEC.md#rules` is a superseded spec, linked from the live set"])

    def test_impact_finds_the_links_and_the_restatements(self):
        # Given
        sut = Impact(self.fixture.specification(), "APP-4")

        # When
        places = [place.describe(self.fixture.root) for place in sut.places()]

        # Then
        self.assertEqual(places, [
            "spec/APP-2/SPEC.md:11: links to APP-1",
            "spec/APP-3/SPEC.md:11: repeats \"a key written twice keeps the\" from APP-1"
        ])

    def test_accept_refuses_until_the_links_are_moved(self):
        # Given
        sut = Acceptance(self.fixture.specification())

        # When
        refused, _ = sut.accept("APP-4")
        self.fixture.write("spec/APP-2/SPEC.md", (self.fixture.root / "spec/APP-2/SPEC.md").read_text().replace("APP-1", "APP-4"))
        findings, changed = Acceptance(self.fixture.specification()).accept("APP-4")

        # Then
        self.assertEqual(len(refused), 1)
        self.assertEqual(findings, [])
        self.assertEqual([(action, path.relative_to(self.fixture.root).as_posix()) for action, path in changed], [
            ("wrote", "spec/APP-4/SPEC.md"),
            ("wrote", "spec/APP-1/SPEC.md")
        ])
        self.assertTrue((self.fixture.root / "spec/APP-1/SPEC.md").read_text().startswith("# APP-1: Title\n\nStatus: accepted\nSuperseded-By: APP-4\n\n## Summary"))
        self.assertEqual(self.fixture.messages(), [])
        self.assertIn("Status: accepted\nSupersedes: APP-1\n", (self.fixture.root / "spec/APP-4/SPEC.md").read_text())
        self.assertEqual([spec.key for spec in self.fixture.specification().live()], ["APP-2", "APP-3", "APP-4"])

    def test_accept_needs_the_template_to_declare_the_mark(self):
        # Given
        self.fixture.declare("Superseded-By: APP-c\n", "")
        self.fixture.write("spec/APP-2/SPEC.md", (self.fixture.root / "spec/APP-2/SPEC.md").read_text().replace("APP-1", "APP-4"))

        # When
        findings, changed = Acceptance(self.fixture.specification()).accept("APP-4")

        # Then
        self.assertEqual([finding.describe(self.fixture.root) for finding in findings], ["spec/TEMPLATE.md: declares `Superseded-By`, since APP-1 is superseded by APP-4"])
        self.assertEqual(changed, [])

    def test_accept_takes_only_a_draft(self):
        # Given
        sut = Acceptance(self.fixture.specification())

        # When
        accepted = lambda: sut.accept("APP-1")

        # Then
        self.assertRaises(Finding, accepted)

    def test_a_pack_holds_the_scope_and_what_it_links_to(self):
        # Given
        self.fixture.write("spec/APP-2/cases/one.json", "{}\n")
        self.fixture.write("spec/review/record/2026-11-08-series.md", "# x\n\n- 1-1, B3, APP-2: a second spelling. reject: one spelling.\n- 1-2, B3, APP-3: other.\n")
        sut = Pack(self.fixture.specification())

        # When
        text = sut.text("series", ["APP-2"], ["A", "B"], report="report.md", probes="probes")
        cases = sut.text("series", ["APP-2"], ["C"])

        # Then
        self.assertIn("Write your report to `report.md`", text)
        self.assertIn("## Criteria you answer: A, B", text)
        self.assertIn("**B1.", text)
        self.assertNotIn("**C1.", text)
        self.assertIn("2026-11-08-series.md: - 1-1, B3, APP-2", text)
        self.assertNotIn("1-2, B3", text)
        self.assertIn("## Linked: APP-1#rules\n\n```md\n## Rules\n\n" + RULE, text)
        self.assertNotIn("## Resource", text)
        self.assertIn("## Resource: spec/APP-2/cases/one.json", cases)
        self.assertRaises(Finding, sut.text, "series", ["APP-2"], ["a"])

    def test_a_pack_of_a_draft_holds_its_reach(self):
        # Given
        sut = Pack(self.fixture.specification())

        # When
        text = sut.text("draft", ["APP-4"], None)

        # Then
        self.assertIn("## Where APP-4 reaches the live set", text)
        self.assertIn("- spec/APP-3/SPEC.md:11: repeats", text)
        self.assertIn("> Here a key written twice keeps the first spelling.", text)

    def test_a_record_starts_with_every_criterion_at_a_clean_commit(self):
        # Given
        self.fixture.git("init", "-q")
        self.fixture.git("add", "-A")
        self.fixture.git("commit", "-qm", "first")
        sut = Record(self.fixture.specification())

        # When
        path = sut.write("draft", ["APP-4"], "2026-11-08")
        text = path.read_text()

        # Then
        self.assertEqual(path.name, "2026-11-08-draft-APP-4.md")
        self.assertTrue(text.startswith("# 2026-11-08 draft\n\nCommit `"))
        self.assertIn("Scope APP-4. Verdict: \n", text)
        self.assertIn("| A1 | | |\n| A2 | | |\n| B0 | | |", text)
        self.assertIn("| E3 | | |\n", text)
        self.assertRaises(Finding, sut.write, "draft", ["APP-4"], "2026-11-08")

    def test_a_record_refuses_changes_not_committed(self):
        # Given
        self.fixture.git("init", "-q")
        self.fixture.git("add", "-A")
        self.fixture.git("commit", "-qm", "first")
        self.fixture.write("spec/APP-3/SPEC.md", "changed\n")

        # When
        sut = Record(self.fixture.specification())

        # Then
        self.assertRaises(Finding, sut.write, "series", ["APP-3"], "2026-11-08")


if __name__ == "__main__":
    unittest.main()
