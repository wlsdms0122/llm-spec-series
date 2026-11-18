import copy
import subprocess

from .finding import Finding
from .series import Series


class Specification:
    """A repository's `spec/`: its README, its review in `review/`, and one
    or more series. `spec/` is a series itself when it holds a `TEMPLATE.md`,
    and so is each folder of it that holds one. A spec is named by its key,
    `<PREFIX>-<n>`, and every prefix is its series' own, so a key names one
    spec in the whole specification.

    The live set is every accepted spec no accepted spec supersedes. It is
    worked out here from all of them and written nowhere."""

    # MARK: - Initializer
    def __init__(self, root):
        self.root = root
        self.directory = root / "spec"
        self.review = self.directory / "review"
        self.series = []
        self.findings = []

        if not self.directory.is_dir():
            raise Finding(self.directory, 0, "a repository keeps its specification in `spec/`")

        children = sorted(
            child for child in self.directory.iterdir()
            if child.is_dir() and not child.name.startswith(".") and child != self.review
        )
        nested = [child for child in children if (child / "TEMPLATE.md").is_file()]

        if (self.directory / "TEMPLATE.md").is_file():
            self.add(self.directory, nested + [self.review])
        else:
            self.findings += [
                Finding(child, 0, "a folder in spec/ is `review/` or a series that holds a `TEMPLATE.md`")
                for child in children if child not in nested
            ]

        for child in nested:
            self.add(child, [])

        if not self.series and not self.findings:
            raise Finding(self.directory, 0, "spec/ holds a series: a `TEMPLATE.md`, or folders that each hold one")

        prefixes = {}

        for series in self.series:
            if series.prefix in prefixes:
                self.findings.append(Finding(series.template.path, 1, f"a prefix names one series, and `{series.prefix}` is also {prefixes[series.prefix].relative_to(root)}"))
            else:
                prefixes[series.prefix] = series.template.path

        self.specs = [spec for series in self.series for spec in series.specs]

    # MARK: - Public
    def spec(self, key):
        return next((spec for spec in self.specs if spec.key == key), None)

    def require(self, key):
        spec = self.spec(key)

        if spec is None:
            raise Finding(self.directory, 0, f"`{key}` is not a spec of the specification")

        return spec

    def commit(self):
        """The commit the specification is read at. Refused while `spec/`
        has changes not committed, other than review records, since then no
        commit is what is read."""

        root = str(self.root)
        head = subprocess.run(["git", "-C", root, "rev-parse", "--short=8", "HEAD"], capture_output=True, text=True)

        if head.returncode != 0:
            raise Finding(self.root, 0, "a review reads a commit, and this is not a git repository with one")

        changes = subprocess.run(
            ["git", "-C", root, "status", "--porcelain", "--", "spec", ":!spec/review/record"],
            capture_output=True,
            text=True
        )

        if changes.stdout.strip():
            raise Finding(self.directory, 0, "has uncommitted changes, so no commit is what the review reads")

        return head.stdout.strip()

    def named(self, prefix):
        return next((series for series in self.series if series.prefix == prefix), None)

    def documents(self):
        documents = [self.directory / "README.md"]
        documents += [document for series in self.series for document in series.documents()]
        documents += [document for spec in self.specs for document in spec.documents()]
        documents += sorted(self.review.rglob("*.md")) if self.review.is_dir() else []

        return list(dict.fromkeys(document for document in documents if document.is_file()))

    def readmes(self):
        readmes = [self.directory / "README.md"] + [series.folder / "README.md" for series in self.series]

        return [readme for readme in dict.fromkeys(readmes) if readme.is_file()]

    def superseders(self):
        superseders = {}

        for spec in self.specs:
            if spec.status == "accepted":
                for key in spec.supersedes:
                    superseders.setdefault(key, []).append(spec.key)

        return superseders

    def live(self):
        superseders = self.superseders()

        return [spec for spec in self.specs if spec.status == "accepted" and spec.key not in superseders]

    def accepting(self, key):
        """This specification as it would stand with the draft `key`
        accepted: its status accepted, and its key
        written under Superseded-By in each spec it supersedes."""

        spec = self.require(key)

        if spec.status != "draft":
            raise Finding(spec.document, spec.places["Status"], f"{key} is accepted already")

        accepted = copy.copy(spec)
        accepted.status = "accepted"
        view = copy.copy(self)
        view.specs = []

        for one in self.specs:
            if one is spec:
                one = accepted
            elif one.key in spec.supersedes:
                one = copy.copy(one)
                one.superseded_by = one.superseded_by + [key]

            view.specs.append(one)

        return view

    # MARK: - Private
    def add(self, folder, excluded):
        try:
            series = Series(folder, self.directory, excluded)
        except Finding as finding:
            self.findings.append(finding)
            return

        self.series.append(series)
        self.findings += series.findings
