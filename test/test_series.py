import unittest

from fixture import SCAFFOLD, Fixture
from series.finding import Finding
from series.markdown import Markdown
from series.scaffold import Scaffold


class SeriesTests(unittest.TestCase):
    # MARK: - Lifecycle
    def setUp(self):
        self.fixture = Fixture()

    def tearDown(self):
        self.fixture.close()

    # MARK: - Test
    def test_a_written_series_passes(self):
        # Given
        self.fixture.spec("APP-1", "accepted", superseded_by="APP-2")
        self.fixture.spec("APP-2", "accepted", supersedes="APP-1")

        # When
        sut = self.fixture.specification()

        # Then
        self.assertEqual(self.fixture.messages(), [])
        self.assertEqual([spec.key for spec in sut.live()], ["APP-2"])

    def test_a_spec_needs_no_resources(self):
        # Given
        self.fixture.spec("APP-1", "accepted")

        # When
        messages = self.fixture.messages()

        # Then
        self.assertEqual(messages, [])

    def test_a_misspelled_supersedes_line_is_refused(self):
        # Given
        self.fixture.spec("APP-1", "accepted")
        self.fixture.spec("APP-2", "accepted", supersedes="APP-1", label="supersedes")

        # When
        messages = self.fixture.messages()

        # Then
        self.assertIn("writes the template's fields, in its order", messages[0])

    def test_a_folder_not_named_as_a_spec_is_refused(self):
        # Given
        (self.fixture.root / "spec" / "app-3").mkdir()

        # When
        messages = self.fixture.messages()

        # Then
        self.assertEqual(messages, ["spec/app-3: a folder in spec/ is `review/`, a series that holds a `TEMPLATE.md`, or a spec named `APP-<n>`"])

    def test_the_next_number_counts_a_folder_that_does_not_read(self):
        # Given
        (self.fixture.root / "spec" / "APP-3").mkdir()

        # When
        sut = self.fixture.specification().series[0]

        # Then
        self.assertEqual(sut.next_number(self.fixture.root), 4)

    def test_the_next_number_counts_a_deleted_draft(self):
        # Given
        self.fixture.git("init", "-q")
        self.fixture.scaffold.draft(self.fixture.specification().series[0], self.fixture.root, "First")
        self.fixture.git("add", "-A")
        self.fixture.git("commit", "-qm", "first")
        self.fixture.git("rm", "-rq", "spec/APP-1")
        self.fixture.git("commit", "-qm", "deleted")

        # When
        sut = self.fixture.scaffold.draft(self.fixture.specification().series[0], self.fixture.root, "Second")

        # Then
        self.assertEqual(sut.parent.name, "APP-2")

    def test_a_draft_passes_and_refuses_an_empty_title(self):
        # Given
        sut = self.fixture.scaffold
        series = self.fixture.specification().series[0]

        # When
        sut.draft(series, self.fixture.root, "A rule")

        # Then
        self.assertEqual(self.fixture.messages(), [])
        self.assertRaises(Finding, sut.draft, series, self.fixture.root, " ")

    def test_an_accepted_spec_leaves_nothing_open(self):
        # Given
        self.fixture.spec("APP-1", "accepted", body="**Open.** Which one.\n")

        # When
        messages = self.fixture.messages()

        # Then
        self.assertEqual(len(messages), 1)

    def test_supersession_names_an_accepted_spec_without_a_circle(self):
        # Given
        self.fixture.spec("APP-1", "accepted", supersedes="APP-2", superseded_by="APP-2")
        self.fixture.spec("APP-2", "accepted", supersedes="APP-1", superseded_by="APP-1")
        self.fixture.spec("APP-3", "draft", superseded_by="APP-4")
        self.fixture.spec("APP-4", "accepted", supersedes="APP-3, APP-4, APP-9", superseded_by="APP-4")

        # When
        messages = self.fixture.messages()

        # Then
        self.assertEqual(messages, [
            "spec/APP-4/SPEC.md:4: supersedes APP-3, which is a draft",
            "spec/APP-4/SPEC.md:4: supersedes itself",
            "spec/APP-4/SPEC.md:4: supersedes APP-9, which is not in the specification",
            "spec/APP-1/SPEC.md:4: supersession runs in a circle: APP-1 > APP-2 > APP-1"
        ])

    def test_links_resolve_and_avoid_the_superseded(self):
        # Given
        self.fixture.spec("APP-1", "accepted", superseded_by="APP-2")
        self.fixture.spec("APP-2", "accepted", supersedes="APP-1", body="See [one](../APP-1/SPEC.md) and [x].\n\n[x]: ../APP-9/SPEC.md\n")

        # When
        messages = self.fixture.messages()

        # Then
        self.assertEqual(len(messages), 2)
        self.assertIn("is a superseded spec", messages[0])
        self.assertIn("resolves to nothing", messages[1])

    def test_a_resource_is_not_a_document_of_the_specification(self):
        # Given
        place = self.fixture.spec("APP-1", "accepted")
        self.fixture.write(place / "cases" / "case-2.md", "[broken](nowhere.md)\n")

        # When
        messages = self.fixture.messages()

        # Then
        self.assertEqual(messages, [])

    def test_fences_and_comments_hide_what_they_hold(self):
        # Given
        text = "~~~~\n```\n## In code\n~~~~\n## Seen\n```\n<!--\n```\n## After code\n<!--\n## Gone\n-->\n## Last\n"

        # When
        sut = Markdown(text)

        # Then
        self.assertEqual([title for _, title in sut.headings(2)], ["Seen", "After code", "Last"])

    def test_a_section_runs_to_the_next_heading_at_its_level(self):
        # Given
        text = "# Top\n\n## One\n\nfirst\n\n### Inner\n\n```\n## not a heading\n```\n\n## Two\n\nsecond\n"

        # When
        sut = Markdown(text).section("one")

        # Then
        self.assertEqual(sut, ["## One", "", "first", "", "### Inner", "", "```", "## not a heading", "```", ""])

    def test_a_field_the_template_declares_is_written_in_its_order(self):
        # Given
        self.fixture.declare("Supersedes: APP-a, APP-b\n", "Supersedes: APP-a, APP-b\nImplementation: <link>\n")
        self.fixture.spec("APP-1", "accepted", extra="Implementation: https://example.com/1")
        self.fixture.spec("APP-2", "accepted", extra="Owner: someone")

        # When
        messages = self.fixture.messages()
        sut = self.fixture.scaffold.draft(self.fixture.specification().series[0], self.fixture.root, "Next").read_text()

        # Then
        self.assertEqual(messages, ["spec/APP-2/SPEC.md:4: writes the template's fields, in its order: Status, Supersedes, Implementation, Superseded-By, Release"])
        self.assertIn("Status: draft\nImplementation: <link>\n\n## Summary", sut)

    def test_a_superseded_spec_says_so_once(self):
        # Given
        self.fixture.spec("APP-1", "accepted")
        self.fixture.spec("APP-2", "accepted", superseded_by="APP-3")
        self.fixture.spec("APP-3", "accepted", supersedes="APP-1")

        # When
        messages = self.fixture.messages()

        # Then
        self.assertEqual(messages, [
            "spec/APP-1/SPEC.md:2: is superseded by APP-3, and says so under `Superseded-By`, once each",
            "spec/APP-2/SPEC.md:4: writes `Superseded-By`, but no accepted spec supersedes it"
        ])

    def test_the_sections_are_the_template_s(self):
        # Given
        self.fixture.declare("## Notes\n", "## Verification\n")
        self.fixture.spec("APP-1", "accepted")

        # When
        messages = self.fixture.messages()

        # Then
        self.assertIn("`## Verification` is next", messages[0])

    def test_the_review_is_read_as_a_document_not_a_spec(self):
        # Given
        self.fixture.write("spec/review/record/2026-11-07-series.md", "[gone](../../APP-1/SPEC.md)\n")

        # When
        messages = self.fixture.messages()

        # Then
        self.assertEqual(messages, ["spec/review/record/2026-11-07-series.md:1: `../../APP-1/SPEC.md` resolves to nothing"])


class SeveralSeriesTests(unittest.TestCase):
    # MARK: - Lifecycle
    def setUp(self):
        self.fixture = Fixture("APP", "app")
        self.fixture.scaffold.write(self.fixture.root, "OPS", "App", "ops")

    def tearDown(self):
        self.fixture.close()

    # MARK: - Test
    def test_each_series_holds_its_own_specs(self):
        # Given
        self.fixture.spec("APP-1", "accepted", folder="app")
        self.fixture.spec("OPS-1", "accepted", folder="ops")
        self.fixture.declare("## Notes\n", "## Runbook\n", folder="ops")

        # When
        messages = self.fixture.messages()
        sut = self.fixture.specification()

        # Then
        self.assertEqual([series.prefix for series in sut.series], ["APP", "OPS"])
        self.assertEqual(messages, ["spec/ops/OPS-1/SPEC.md:16: holds the template's sections in order, and `## Runbook` is next"])

    def test_a_spec_supersedes_one_of_another_series(self):
        # Given
        self.fixture.spec("APP-1", "accepted", folder="app", superseded_by="OPS-1")
        self.fixture.spec("OPS-1", "accepted", supersedes="APP-1", folder="ops")

        # When
        sut = self.fixture.specification()

        # Then
        self.assertEqual(self.fixture.messages(), [])
        self.assertEqual([spec.key for spec in sut.live()], ["OPS-1"])

    def test_a_folder_beside_the_series_is_refused(self):
        # Given
        (self.fixture.root / "spec" / "notes").mkdir()
        (self.fixture.root / "spec" / "app" / "APP-x").mkdir()

        # When
        messages = self.fixture.messages()

        # Then
        self.assertEqual(messages, [
            "spec/notes: a folder in spec/ is `review/` or a series that holds a `TEMPLATE.md`",
            "spec/app/APP-x: a folder in a series is a spec named `APP-<n>`"
        ])

    def test_a_prefix_names_one_series(self):
        # Given
        sut = Scaffold(SCAFFOLD)

        # When
        written = lambda folder: sut.write(self.fixture.root, "NEW" if folder != "more" else "OPS", "App", folder)

        # Then
        for folder in ("more", "review", "a/b", "../x", ".hidden"):
            self.assertRaises(Finding, written, folder)


if __name__ == "__main__":
    unittest.main()
