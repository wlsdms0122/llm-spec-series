from .finding import Finding
from .lint import Lint
from .spec import RELEASE


class Release:
    """Cutting a release: every accepted spec that does not say which release
    it entered says this one, under Release. Each series whose template
    declares Release is written, and the cut is refused while the
    specification has a lint finding."""

    # MARK: - Initializer
    def __init__(self, specification):
        self.specification = specification

    # MARK: - Public
    def cut(self, name):
        if not RELEASE.fullmatch(name):
            raise Finding(self.specification.root, 0, f"a release is named in one word, and `{name}` is not")

        series = [one for one in self.specification.series if "Release" in one.template.fields]

        if not series:
            raise Finding(self.specification.directory, 0, "a release is written by a series whose template declares `Release`, and none does")

        findings = Lint(self.specification).findings()

        if findings:
            return findings, []

        changed = []

        for spec in (spec for one in series for spec in one.specs):
            if spec.status == "accepted" and spec.release is None:
                spec.document.write_text("\n".join(spec.released(name)), encoding="utf-8")
                changed.append(("wrote", spec.document))

        return [], changed
