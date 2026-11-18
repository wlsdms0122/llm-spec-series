import unittest

from fixture import Fixture
from series.finding import Finding
from series.history import History
from series.release import Release


class ReleaseTests(unittest.TestCase):
    # MARK: - Lifecycle
    def setUp(self):
        self.fixture = Fixture()

    def tearDown(self):
        self.fixture.close()

    # MARK: - Test
    def test_a_draft_writes_no_release(self):
        # Given
        self.fixture.spec("APP-1", "accepted", extra="Release: 1.0")
        self.fixture.spec("APP-2", "draft", extra="Release: 1.0")

        # When
        messages = self.fixture.messages()

        # Then
        self.assertEqual(messages, ["spec/APP-2/SPEC.md:4: a draft enters no release, so it writes no `Release`"])

    def test_a_release_is_one_word(self):
        # Given
        self.fixture.spec("APP-1", "accepted", extra="Release: one point zero")

        # When
        messages = self.fixture.messages()

        # Then
        self.assertEqual(messages, ["spec/APP-1/SPEC.md:4: writes `Release: <release>`, the release's name in one word"])

    def test_a_draft_starts_without_a_release(self):
        # Given
        series = self.fixture.specification().series[0]

        # When
        sut = self.fixture.scaffold.draft(series, self.fixture.root, "Next").read_text()

        # Then
        self.assertIn("Status: draft\n\n## Summary", sut)

    def test_a_release_is_written_into_each_accepted_spec_that_names_none(self):
        # Given
        self.fixture.spec("APP-1", "accepted", extra="Release: 1.0")
        self.fixture.spec("APP-2", "accepted", superseded_by="APP-3")
        self.fixture.spec("APP-3", "accepted", supersedes="APP-2")
        self.fixture.spec("APP-4", "draft")

        # When
        findings, changed = Release(self.fixture.specification()).cut("1.1")

        # Then
        self.assertEqual(findings, [])
        self.assertEqual([path.parent.name for _, path in changed], ["APP-2", "APP-3"])
        self.assertTrue((self.fixture.root / "spec/APP-2/SPEC.md").read_text().startswith("# APP-2: Title\n\nStatus: accepted\nSuperseded-By: APP-3\nRelease: 1.1\n\n## Summary"))
        self.assertTrue((self.fixture.root / "spec/APP-3/SPEC.md").read_text().startswith("# APP-3: Title\n\nStatus: accepted\nSupersedes: APP-2\nRelease: 1.1\n\n## Summary"))
        self.assertIn("Release: 1.0\n", (self.fixture.root / "spec/APP-1/SPEC.md").read_text())
        self.assertNotIn("Release", (self.fixture.root / "spec/APP-4/SPEC.md").read_text())
        self.assertEqual(self.fixture.messages(), [])

    def test_a_release_is_refused_while_lint_finds_anything(self):
        # Given
        self.fixture.spec("APP-1", "accepted", body="**Open.** Which one.\n")

        # When
        findings, changed = Release(self.fixture.specification()).cut("1.0")

        # Then
        self.assertEqual(len(findings), 1)
        self.assertEqual(changed, [])
        self.assertNotIn("Release", (self.fixture.root / "spec/APP-1/SPEC.md").read_text())

    def test_a_release_needs_a_template_that_declares_it(self):
        # Given
        self.fixture.declare("Release: 1.0\n", "")
        self.fixture.spec("APP-1", "accepted")
        sut = Release(self.fixture.specification())

        # Then
        self.assertRaises(Finding, sut.cut, "1.0")
        self.assertRaises(Finding, Release(self.fixture.specification()).cut, "1 0")

    def test_a_history_tells_each_release_where_the_spec_moved(self):
        # Given
        self.fixture.git("init", "-q")
        self.fixture.spec("APP-1", "accepted", extra="Release: 1.0")
        self.commit("1.0")
        self.fixture.spec("APP-2", "draft")
        self.commit("1.1")
        self.fixture.write("spec/APP-1/SPEC.md", (self.fixture.root / "spec/APP-1/SPEC.md").read_text().replace("Release: 1.0\n", "Superseded-By: APP-2\nRelease: 1.0\n"))
        self.fixture.write("spec/APP-2/SPEC.md", (self.fixture.root / "spec/APP-2/SPEC.md").read_text().replace("Status: draft\n", "Status: accepted\nSupersedes: APP-1\nRelease: 2.0\n"))
        self.commit("2.0")
        sut = History(self.fixture.specification())

        # When
        first, second = sut.releases("APP-1"), sut.releases("APP-2")

        # Then
        self.assertEqual(first, [("1.0", "accepted"), ("2.0", "superseded by APP-2")])
        self.assertEqual(second, [("1.1", "draft"), ("2.0", "accepted")])

    # MARK: - Private
    def commit(self, tag):
        self.fixture.git("add", "-A")
        self.fixture.git("commit", "-qm", tag)
        self.fixture.git("tag", tag)
