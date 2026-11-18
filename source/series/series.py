import re
import subprocess

from .finding import Finding
from .spec import Spec
from .template import Template


class Series:
    """A folder that holds a `TEMPLATE.md`, and the specs in the folders
    beside it. The template's prefix is the series' key: every spec in it is
    named `<PREFIX>-<n>`, and `n` is the next number free in the series when
    the spec is drafted."""

    # MARK: - Initializer
    def __init__(self, folder, specification, excluded=()):
        self.folder = folder
        self.specification = specification
        self.excluded = set(excluded)
        self.template = Template(folder / "TEMPLATE.md")
        self.prefix = self.template.prefix
        self.specs = []
        self.findings = []

        for child in self.folders():
            number = Spec.number(child.name, self.prefix)

            if number is None:
                self.findings.append(Finding(child, 0, self.stray()))
                continue

            try:
                self.specs.append(Spec(child, number, self.template))
            except Finding as finding:
                self.findings.append(finding)

        self.specs.sort(key=lambda spec: spec.number)

    # MARK: - Public
    def folders(self):
        return sorted(
            child for child in self.folder.iterdir()
            if child.is_dir() and not child.name.startswith(".") and child not in self.excluded
        )

    def documents(self):
        documents = [self.template.path, self.folder / "README.md"]

        return [document for document in documents if document.is_file()]

    def next_number(self, root):
        written = {Spec.number(folder.name, self.prefix) for folder in self.folders()}

        return max((written | self.numbers_in_history(root)) - {None}, default=0) + 1

    # MARK: - Private
    def stray(self):
        if self.folder == self.specification:
            return f"a folder in spec/ is `review/`, a series that holds a `TEMPLATE.md`, or a spec named `{self.prefix}-<n>`"

        return f"a folder in a series is a spec named `{self.prefix}-<n>`"

    def numbers_in_history(self, root):
        place = self.folder.relative_to(root).as_posix()
        written = subprocess.run(
            ["git", "-C", str(root), "log", "--all", "--format=", "--name-only", "--relative", "--", place],
            capture_output=True,
            text=True
        )

        if written.returncode != 0:
            return set()

        folders = re.findall(rf"^{re.escape(place)}/([^/\n]+)/", written.stdout, re.MULTILINE)

        return {Spec.number(folder, self.prefix) for folder in folders}
