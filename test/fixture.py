import pathlib
import subprocess
import sys
import tempfile

sys.path.insert(0, str(pathlib.Path(__file__).resolve().parent.parent / "source"))

from series.lint import Lint
from series.scaffold import Scaffold
from series.specification import Specification

SCAFFOLD = pathlib.Path(__file__).resolve().parent.parent / "scaffold"
SECTIONS = "## Summary\n\n## Motivation\n\n## Rules\n\n## Interactions\n\n## Alternatives considered\n\n## Notes\n"


class Fixture:
    """A repository with a specification written by the scaffold, and specs
    written by hand into it."""

    # MARK: - Initializer
    def __init__(self, prefix="APP", folder=None):
        self.directory = tempfile.TemporaryDirectory()
        self.root = pathlib.Path(self.directory.name)
        self.scaffold = Scaffold(SCAFFOLD)
        self.scaffold.write(self.root, prefix, "App", folder)

    # MARK: - Public
    def close(self):
        self.directory.cleanup()

    def specification(self):
        return Specification(self.root)

    def messages(self, accepting=None):
        specification = self.specification()
        view = specification.accepting(accepting) if accepting else specification

        return [finding.describe(self.root) for finding in Lint(view).findings()]

    def declare(self, old, new, folder=None):
        template = self.root / "spec" / (folder or "") / "TEMPLATE.md"
        template.write_text(template.read_text().replace(old, new))

    def spec(self, key, status, supersedes=None, label="Supersedes", extra=None, body="", folder=None, superseded_by=None):
        place = self.root / "spec" / (folder or "") / key
        head = f"# {key}: Title\n\nStatus: {status}\n"
        head += f"{label}: {supersedes}\n" if supersedes else ""
        head += f"{extra}\n" if extra else ""
        head += f"Superseded-By: {superseded_by}\n" if superseded_by else ""
        place.mkdir()
        sections = SECTIONS.replace("## Rules\n", "## Rules\n\n" + body)
        (place / "SPEC.md").write_text(f"{head}\n{sections}")

        return place

    def write(self, path, text):
        target = self.root / path
        target.parent.mkdir(parents=True, exist_ok=True)
        target.write_text(text)

        return target

    def git(self, *arguments):
        subprocess.run(
            ["git", "-C", str(self.root), "-c", "user.name=test", "-c", "user.email=test@example.com", *arguments],
            check=True
        )
