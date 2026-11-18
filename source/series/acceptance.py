from .lint import Lint


class Acceptance:
    """Accepting a draft, once it has been judged: its status becomes
    `accepted`, and each spec it supersedes says so under Superseded-By. It is
    refused while the specification, read as if the draft were accepted, has
    a lint finding."""

    # MARK: - Initializer
    def __init__(self, specification):
        self.specification = specification

    # MARK: - Public
    def accept(self, key):
        view = self.specification.accepting(key)
        findings = Lint(view).findings()

        if findings:
            return findings, []

        spec = self.specification.spec(key)
        lines = spec.document.read_text(encoding="utf-8").split("\n")
        lines[spec.places["Status"] - 1] = "Status: accepted"
        spec.document.write_text("\n".join(lines), encoding="utf-8")
        changed = [("wrote", spec.document)]

        for target in spec.supersedes:
            superseded = self.specification.spec(target)
            superseded.document.write_text("\n".join(superseded.marked(key)), encoding="utf-8")
            changed.append(("wrote", superseded.document))

        return [], changed
