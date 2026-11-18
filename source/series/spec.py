import re

from .finding import Finding

STATUSES = ("draft", "accepted")
SUPERSESSION = ("Supersedes", "Superseded-By")
KEY = re.compile(r"(\S+)-([1-9][0-9]*)")
RELEASE = re.compile(r"\S+")


class Spec:
    """One spec of a series, read from its head:

        # <PREFIX>-<n>: <title>

        Status: draft | accepted
        Supersedes: <KEY>, <KEY>
        Superseded-By: <KEY>, <KEY>
        Release: <release>
        ...

    The lines under the blank are fields its series' template declares, in
    the template's order. Status is required and the rest are written when
    they apply. Supersedes is written by the spec that replaces others, and
    Superseded-By by `accept` into each spec it replaced, so a superseded spec
    says so where it is read. Release is written by `release` into each
    accepted spec when the release it enters is cut."""

    # MARK: - Initializer
    def __init__(self, folder, number, template):
        document = folder / "SPEC.md"

        if not document.is_file():
            raise Finding(folder, 0, "a spec's folder holds a `SPEC.md`")

        key = Spec.key(template.prefix, number)
        lines = document.read_text(encoding="utf-8").split("\n")
        heading = f"# {key}: "

        if not lines[0].startswith(heading) or not lines[0][len(heading):].strip():
            raise Finding(document, 1, f"opens with `{heading}<title>`")

        if len(lines) < 3 or lines[1] != "":
            raise Finding(document, 2, "leaves a blank line under its heading, then its fields")

        fields = {}
        places = {}

        for index in range(2, len(lines)):
            if lines[index] == "":
                break

            name, separator, value = lines[index].partition(": ")
            written = [template.fields.index(one) for one in fields]

            if not separator or name not in template.fields or name in fields or (written and template.fields.index(name) < max(written)):
                raise Finding(document, index + 1, f"writes the template's fields, in its order: {', '.join(template.fields)}")

            fields[name] = value
            places[name] = index + 1

        if fields.get("Status") not in STATUSES:
            raise Finding(document, places.get("Status", 3), "says `Status: draft` or `Status: accepted`")

        supersedes, superseded_by = (Spec.keys(document, fields, places, name) for name in SUPERSESSION)

        if "Release" in fields and not RELEASE.fullmatch(fields["Release"]):
            raise Finding(document, places["Release"], "writes `Release: <release>`, the release's name in one word")

        self.key = key
        self.number = number
        self.title = lines[0][len(heading):]
        self.status = fields["Status"]
        self.supersedes = supersedes
        self.superseded_by = superseded_by
        self.release = fields.get("Release")
        self.places = places
        self.template = template
        self.folder = folder
        self.document = document

    # MARK: - Public
    @staticmethod
    def number(name, prefix):
        match = KEY.fullmatch(name)

        return int(match.group(2)) if match and match.group(1) == prefix else None

    @staticmethod
    def key(prefix, number):
        return f"{prefix}-{number}"

    @staticmethod
    def keys(document, fields, places, name):
        keys = fields[name].split(", ") if name in fields else []

        if any(not KEY.fullmatch(one) for one in keys):
            raise Finding(document, places[name], f"writes `{name}: <PREFIX>-<a>, <PREFIX>-<b>`")

        return keys

    @staticmethod
    def heading(document, key, title):
        if not title.strip() or "\n" in title or title != title.strip():
            raise Finding(document, 1, "a spec's title is one line of text")

        return f"# {key}: {title}"

    def marked(self, key):
        """The lines of this spec's document with `key` written under
        Superseded-By."""

        return self.written("Superseded-By", ", ".join(self.superseded_by + [key]))

    def released(self, name):
        """The lines of this spec's document saying it entered the release
        `name`."""

        return self.written("Release", name)

    def documents(self):
        return [self.document]

    def resources(self):
        return sorted(
            path
            for child in self.folder.iterdir() if child.is_dir() and not child.name.startswith(".")
            for path in child.rglob("*") if path.is_file() and not path.name.startswith(".")
        )

    # MARK: - Private
    def written(self, field, value):
        """The lines of this spec's document with `field` set to `value`,
        the field placed where its template orders it."""

        lines = self.document.read_text(encoding="utf-8").split("\n")

        if field in self.places:
            lines[self.places[field] - 1] = f"{field}: {value}"
        else:
            order = self.template.fields.index(field)
            before = [line for name, line in self.places.items() if self.template.fields.index(name) < order]
            lines.insert(max(before, default=2), f"{field}: {value}")

        return lines
