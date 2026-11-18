import re

FENCE = re.compile(r"^ {0,3}(`{3,}|~{3,})(.*)$")
CODE_SPAN = re.compile(r"`+[^`]*`+")
INLINE = re.compile(r"\[[^\]]*\]\(\s*(<[^>]*>|[^)\s]+)")
DEFINITION = re.compile(r"^ {0,3}\[[^\]]+\]:\s*(<[^>]*>|\S+)")
WRITTEN_LINK = re.compile(r"\[([^\]]*)\]\([^)]*\)")
HEADING = re.compile(r"^(#{1,6})\s+(.*?)\s*#*\s*$")


class Markdown:
    """A markdown file read for its prose: fenced code and HTML comments are
    not prose, so their headings and links are not headings and links."""

    # MARK: - Initializer
    def __init__(self, text):
        self.text = text.split("\n")
        self.lines = []
        fence = None
        commented = False

        for number, line in enumerate(text.split("\n"), start=1):
            if fence:
                match = FENCE.match(line)

                if match and match.group(1)[0] == fence[0] and len(match.group(1)) >= len(fence) and not match.group(2).strip():
                    fence = None

                continue

            if not commented and (match := FENCE.match(line)):
                fence = match.group(1)
                continue

            line, commented = self.uncomment(line, commented)
            self.lines.append((number, line))

    # MARK: - Public
    def headings(self, level):
        marks = "#" * level

        return [
            (number, match.group(2))
            for number, line in self.lines
            if (match := HEADING.match(line)) and match.group(1) == marks
        ]

    def anchors(self):
        return {anchor for _, _, anchor in self.anchored()}

    def section(self, anchor):
        """The lines of the section the anchor names, its heading first, up
        to the next heading at its level or above, as written."""

        anchored = self.anchored()
        start = next(((number, level) for number, level, one in anchored if one == anchor), None)

        if start is None:
            return []

        number, level = start
        end = next((one for one, other, _ in anchored if one > number and other <= level), len(self.text) + 1)

        return self.text[number - 1:end - 1]

    def spans(self):
        return [(number, CODE_SPAN.findall(line)) for number, line in self.lines]

    def links(self):
        links = []

        for number, line in self.lines:
            prose = CODE_SPAN.sub("", line)
            targets = [match.group(1) for match in INLINE.finditer(prose)]

            if definition := DEFINITION.match(prose):
                targets.append(definition.group(1))

            links += [(number, target.removeprefix("<").removesuffix(">")) for target in targets]

        return links

    def find(self, text):
        return next((number for number, line in self.lines if text in CODE_SPAN.sub("", line)), None)

    # MARK: - Private
    def anchored(self):
        anchored = []
        counts = {}

        for number, line in self.lines:
            if match := HEADING.match(line):
                slug = self.slug(match.group(2))
                count = counts.get(slug, 0)
                counts[slug] = count + 1
                anchored.append((number, len(match.group(1)), slug if count == 0 else f"{slug}-{count}"))

        return anchored

    def uncomment(self, line, commented):
        kept = ""

        while line:
            if commented:
                end = line.find("-->")

                if end < 0:
                    return kept, True

                line = line[end + 3:]
                commented = False
            else:
                start = line.find("<!--")

                if start < 0:
                    return kept + line, False

                kept += line[:start]
                line = line[start + 4:]
                commented = True

        return kept, commented

    def slug(self, heading):
        text = WRITTEN_LINK.sub(lambda match: match.group(1), heading)

        return re.sub(r"[^\w\- ]", "", text.strip().lower()).replace(" ", "-")
