import re

from .finding import Finding

GROUP = re.compile(r"^## ([A-Z])\. ")
CRITERION = re.compile(r"^\s*- \*\*([A-Z][0-9]+)\.")


class Criteria:
    """A specification's acceptance criteria, `review/CRITERIA.md`: groups
    headed `## <letter>. <title>`, each holding criteria written
    `- **<letter><n>. ...`."""

    # MARK: - Initializer
    def __init__(self, path):
        if not path.is_file():
            raise Finding(path, 0, "a review judges by its criteria, and this file is not there")

        self.path = path
        self.lines = path.read_text(encoding="utf-8").split("\n")
        self.groups = [match.group(1) for line in self.lines if (match := GROUP.match(line))]
        self.criteria = [match.group(1) for line in self.lines if (match := CRITERION.match(line))]

    # MARK: - Public
    def text(self, groups=None):
        """The criteria as written, keeping only the groups named, and every
        part of the file that is not a group."""

        if groups is None:
            return "\n".join(self.lines)

        unknown = [group for group in groups if group not in self.groups]

        if unknown:
            raise Finding(self.path, 0, f"has the groups {', '.join(self.groups)}, and not {', '.join(unknown)}")

        kept = []
        keeping = True

        for line in self.lines:
            if line.startswith("## "):
                match = GROUP.match(line)
                keeping = match is None or match.group(1) in groups

            if keeping:
                kept.append(line)

        return "\n".join(kept)
