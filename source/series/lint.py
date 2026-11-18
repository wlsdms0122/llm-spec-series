import re

from .finding import Finding
from .markdown import Markdown

SCHEME = re.compile(r"[A-Za-z][A-Za-z0-9+.-]*:")


class Lint:
    """What a specification's own rules make checkable without judgement:
    each spec's head and sections, what it supersedes, what an accepted spec
    no longer holds, that a draft entered no release, and the links between
    the documents."""

    # MARK: - Initializer
    def __init__(self, specification):
        self.specification = specification
        self.documents = {}

    # MARK: - Public
    def findings(self):
        findings = list(self.specification.findings)

        for spec in self.specification.specs:
            findings += self.supersedes(spec)
            findings += self.sections(spec)

            if spec.status == "accepted":
                findings += self.accepted(spec)
            elif spec.release is not None:
                findings.append(Finding(spec.document, spec.places["Release"], "a draft enters no release, so it writes no `Release`"))

        findings += self.marks()
        findings += self.cycles()
        findings += self.links()

        return findings

    # MARK: - Private
    def supersedes(self, spec):
        findings = []
        line = spec.places.get("Supersedes")

        for key in spec.supersedes:
            target = self.specification.spec(key)

            if key == spec.key:
                findings.append(Finding(spec.document, line, "supersedes itself"))
            elif target is None:
                findings.append(Finding(spec.document, line, f"supersedes {key}, which is not in the specification"))
            elif target.status == "draft":
                findings.append(Finding(spec.document, line, f"supersedes {key}, which is a draft"))

        if len(set(spec.supersedes)) != len(spec.supersedes):
            findings.append(Finding(spec.document, line, "names a spec under Supersedes more than once"))

        return findings

    def marks(self):
        findings = []
        superseders = self.specification.superseders()

        for spec in self.specification.specs:
            by = superseders.get(spec.key, [])
            line = spec.places.get("Superseded-By", 0)

            if by and "Superseded-By" not in spec.template.fields:
                findings.append(Finding(spec.template.path, 0, f"declares `Superseded-By`, since {spec.key} is superseded by {', '.join(by)}"))
            elif sorted(spec.superseded_by) == sorted(by) and len(set(spec.superseded_by)) == len(spec.superseded_by):
                continue
            elif by:
                findings.append(Finding(spec.document, line or 2, f"is superseded by {', '.join(by)}, and says so under `Superseded-By`, once each"))
            else:
                findings.append(Finding(spec.document, line, "writes `Superseded-By`, but no accepted spec supersedes it"))

        return findings

    def cycles(self):
        findings = []
        edges = {spec.key: [key for key in spec.supersedes if key != spec.key] for spec in self.specification.specs}
        state = {}

        def visit(key, path):
            state[key] = "open"

            for next_key in edges.get(key, []):
                if state.get(next_key) == "open":
                    cycle = path[path.index(next_key):] + [next_key]
                    spec = self.specification.spec(next_key)
                    findings.append(Finding(spec.document, spec.places.get("Supersedes"), f"supersession runs in a circle: {' > '.join(cycle)}"))
                elif next_key not in state:
                    visit(next_key, path + [next_key])

            state[key] = "closed"

        for key in edges:
            if key not in state:
                visit(key, [key])

        return findings

    def sections(self, spec):
        headings = self.markdown(spec.document).headings(2)
        sections = spec.template.sections

        for index, title in enumerate(sections):
            if index >= len(headings) or headings[index][1] != title:
                line = headings[index][0] if index < len(headings) else 0

                return [Finding(spec.document, line, f"holds the template's sections in order, and `## {title}` is next")]

        if len(headings) > len(sections):
            line, title = headings[len(sections)]

            return [Finding(spec.document, line, f"`## {title}` is not a section of the template")]

        return []

    def accepted(self, spec):
        findings = []
        open_line = self.markdown(spec.document).find("**Open.**")

        if open_line:
            findings.append(Finding(spec.document, open_line, "an accepted spec leaves nothing open"))

        return findings

    def links(self):
        findings = []
        root = self.specification.root.resolve()
        superseders = self.specification.superseders()
        superseded = [spec.folder.resolve() for spec in self.specification.specs if spec.key in superseders]
        live = {spec.document for spec in self.specification.live()} | set(self.specification.readmes())

        for document in self.specification.documents():
            for line, target in self.markdown(document).links():
                if SCHEME.match(target):
                    continue

                path, _, anchor = target.partition("#")
                resolved = (document.parent / path).resolve() if path else document.resolve()

                if not resolved.is_relative_to(root):
                    findings.append(Finding(document, line, f"`{target}` points outside the repository"))
                elif not resolved.exists():
                    findings.append(Finding(document, line, f"`{target}` resolves to nothing"))
                elif anchor and resolved.suffix == ".md" and anchor not in self.markdown(resolved).anchors():
                    findings.append(Finding(document, line, f"`{target}` names a heading its document does not have"))
                elif document in live and any(resolved.is_relative_to(folder) for folder in superseded):
                    findings.append(Finding(document, line, f"`{target}` is a superseded spec, linked from the live set"))

        return findings

    def markdown(self, path):
        if path not in self.documents:
            self.documents[path] = Markdown(path.read_text(encoding="utf-8"))

        return self.documents[path]
