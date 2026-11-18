import re

from .finding import Finding
from .spec import Spec

COMMENT = re.compile(r"\n<!--.*?-->\n", re.DOTALL)


class Scaffold:
    """The documents a specification starts from, written into a repository
    once. From then on they are the repository's own. The specification's
    README and review are written with its first series, and a series is its
    template: `spec/TEMPLATE.md`, or `spec/<folder>/TEMPLATE.md` for each
    series after."""

    # MARK: - Initializer
    def __init__(self, source):
        self.source = source

    # MARK: - Public
    def write(self, root, prefix, name, folder):
        directory = root / "spec"
        template = (directory / folder if folder else directory) / "TEMPLATE.md"
        taken = self.prefixes(directory)
        files = []

        if folder is not None and (not re.fullmatch(r"[^/\\.][^/\\]*", folder) or folder == "review"):
            raise Finding(root, 0, f"a series' folder is one folder of spec/ other than review/, and `{folder}` is not")

        if not re.fullmatch(r"[A-Z][A-Z0-9]*", prefix):
            raise Finding(root, 0, f"a prefix is capital letters and digits, and `{prefix}` is not")

        if prefix in taken:
            raise Finding(taken[prefix], 1, f"`{prefix}` names this series already")

        if template.exists():
            raise Finding(template, 0, "is already there, and a scaffold writes over nothing")

        if not (directory / "README.md").exists():
            source = self.source / "spec"
            files += [
                (path, directory / path.relative_to(source))
                for path in sorted(source.rglob("*"))
                if path.is_file() and path.name != "TEMPLATE.md"
            ]

        files.append((self.source / "spec" / "TEMPLATE.md", template))
        taken_files = [target for _, target in files if target.exists()]

        if taken_files:
            raise Finding(taken_files[0], 0, "is already there, and a scaffold writes over nothing")

        for path, target in files:
            target.parent.mkdir(parents=True, exist_ok=True)
            target.write_text(
                path.read_text(encoding="utf-8").replace("{{PREFIX}}", prefix).replace("{{NAME}}", name),
                encoding="utf-8"
            )

        return [target for _, target in files]

    def draft(self, series, root, title):
        number = series.next_number(root)
        key = Spec.key(series.prefix, number)
        folder = series.folder / key
        document = folder / "SPEC.md"
        template = series.template
        fields = ["Status: draft" if line.startswith("Status: ") else line for line in template.head if not line.startswith(("Supersedes: ", "Superseded-By: ", "Release: "))]
        head = "\n".join([Spec.heading(document, key, title), ""] + fields)
        text = re.sub(r"\n{3,}", "\n\n", head + "\n" + COMMENT.sub("\n", template.body))

        folder.mkdir()
        document.write_text(text, encoding="utf-8")

        return document

    # MARK: - Private
    def prefixes(self, directory):
        templates = [directory / "TEMPLATE.md"] + sorted(directory.glob("*/TEMPLATE.md")) if directory.is_dir() else []
        prefixes = {}

        for template in templates:
            if template.is_file() and (match := re.match(r"# (\S+)-N: ", template.read_text(encoding="utf-8"))):
                prefixes[match.group(1)] = template

        return prefixes
