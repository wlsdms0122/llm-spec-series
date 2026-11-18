import re

from .criteria import Criteria
from .impact import Impact
from .markdown import Markdown

BACKTICKS = re.compile(r"`+")


class Pack:
    """Everything one reviewer reads, in one file: where to write, the brief,
    the criteria it answers, how the specification works, the record lines on
    its scope, the scope whole with its resources, the sections it links to
    outside the scope, and what the coordinator ran beforehand. It is built
    from the repository at the commit, so no reviewer is briefed in words the
    repository does not hold."""

    # MARK: - Initializer
    def __init__(self, specification):
        self.specification = specification

    # MARK: - Public
    def text(self, mode, keys, groups=None, attachments=(), report=None, probes=None, commit=None):
        specs = [self.specification.require(key) for key in keys]
        review = self.specification.review
        parts = [f"# Review pack\n\nMode `{mode}`. Scope {', '.join(spec.key for spec in specs)}." + (f" Commit `{commit}`." if commit else "")]
        output = []

        if report:
            output.append(f"Write your report to `{report}`, and nothing else in any repository.")

        if probes:
            output.append(f"Write each probe as one file under `{probes}`, in the format a case is written in, named for what it asks. The coordinator runs them and reads the lines the runner prints.")

        if output:
            parts.append("## Where you write\n\n" + "\n\n".join(output))

        parts.append(self.document("Brief", review / "REVIEWER.md"))
        parts.append(self.criteria(groups))

        for readme in self.readmes(specs):
            parts.append(self.document(f"How the specification works: {readme.relative_to(self.specification.root)}", readme))

        parts.append(self.records(specs))

        for spec in specs:
            for document in spec.documents():
                parts.append(self.document(f"Scope: {document.relative_to(self.specification.root)}", document))

        for spec in specs:
            if spec.status == "draft":
                parts.append(self.reach(spec))

        if groups is None or "C" in groups:
            parts.append(self.resources(specs))

        parts.append(self.linked(specs))

        for attachment in attachments:
            parts.append(self.document(f"Ran beforehand: {attachment.name}", attachment))

        return "\n\n".join(part for part in parts if part) + "\n"

    # MARK: - Private
    def reach(self, spec):
        places = Impact(self.specification, spec.key).places()
        lines = []

        for place in places:
            text = place.path.read_text(encoding="utf-8").split("\n")[place.line - 1].strip()
            lines.append(f"- {place.describe(self.specification.root)}\n  > {text}")

        body = "\n".join(lines) if lines else "None."

        return f"## Where {spec.key} reaches the live set\n\nFound from the text by `spec-series impact`: places to look, not findings.\n\n{body}"

    def readmes(self, specs):
        folders = {spec.folder.parent for spec in specs}

        return [readme for readme in self.specification.readmes() if readme.parent == self.specification.directory or readme.parent in folders]

    def criteria(self, groups):
        criteria = Criteria(self.specification.review / "CRITERIA.md")
        title = "Criteria" if groups is None else f"Criteria you answer: {', '.join(groups)}"

        return self.fenced(title, "md", criteria.text(groups))

    def records(self, specs):
        directory = self.specification.review / "record"
        lines = []

        for path in sorted(directory.glob("*.md")) if directory.is_dir() else []:
            for line in path.read_text(encoding="utf-8").split("\n"):
                if line.startswith("- ") and any(re.search(rf"(?<![\w-]){re.escape(spec.key)}(?![\w-])", line) for spec in specs):
                    lines.append(f"{path.name}: {line}")

        return "## Record lines on the scope\n\n" + ("\n".join(lines) if lines else "None.")

    def resources(self, specs):
        parts = []

        for spec in specs:
            for path in spec.resources():
                parts.append(self.document(f"Resource: {path.relative_to(self.specification.root)}", path))

        return "\n\n".join(parts)

    def linked(self, specs):
        scope = {spec.document for spec in specs}
        folders = [(spec.folder.resolve(), spec) for spec in self.specification.specs if spec.document not in scope]
        parts = []
        seen = set()

        for spec in specs:
            for document in spec.documents():
                for _, target in Markdown(document.read_text(encoding="utf-8")).links():
                    path, _, anchor = target.partition("#")
                    resolved = (document.parent / path).resolve() if path else None

                    if not resolved or not anchor or (resolved, anchor) in seen:
                        continue

                    owner = next((one for folder, one in folders if resolved == one.document.resolve()), None)

                    if owner:
                        seen.add((resolved, anchor))
                        section = "\n".join(Markdown(resolved.read_text(encoding="utf-8")).section(anchor))
                        parts.append(self.fenced(f"Linked: {owner.key}#{anchor}", "md", section))

        return "\n\n".join(parts)

    def document(self, title, path):
        try:
            text = path.read_text(encoding="utf-8")
        except UnicodeDecodeError:
            return f"## {title}\n\nNot text, {path.stat().st_size} bytes."

        return self.fenced(title, path.suffix.lstrip(".") or "text", text)

    def fenced(self, title, kind, text):
        fence = "`" * max(3, max((len(run) for run in BACKTICKS.findall(text)), default=0) + 1)

        return f"## {title}\n\n{fence}{kind}\n{text.rstrip()}\n{fence}"
