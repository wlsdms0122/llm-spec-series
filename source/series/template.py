import re

from .finding import Finding
from .markdown import Markdown


class Template:
    """A series' template, which is where the series says what every spec
    holds. Its heading gives the prefix, the lines under it give the fields a
    head may write, and its `##` headings give the sections:

        # <PREFIX>-N: Title

        Status: draft
        <Field>: <value>
        ...

        ## <Section>
        ...

    Status is the one field the template must declare, since whether a spec
    counts is read from it."""

    # MARK: - Initializer
    def __init__(self, path):
        if not path.is_file():
            raise Finding(path, 0, "a series has a template")

        text = path.read_text(encoding="utf-8")
        lines = text.split("\n")
        match = re.fullmatch(r"# (\S+)-N: .+", lines[0])

        if not match:
            raise Finding(path, 1, "the template opens with `# <PREFIX>-N: <title>`")

        if len(lines) < 3 or lines[1] != "":
            raise Finding(path, 2, "the template leaves a blank line under its heading, then its fields")

        end = next((index for index in range(2, len(lines)) if lines[index] == ""), len(lines))
        fields = [line.partition(": ") for line in lines[2:end]]

        if any(not separator for _, separator, _ in fields):
            raise Finding(path, 3, "the template writes each field as `<Field>: <value>`")

        self.path = path
        self.prefix = match.group(1)
        self.fields = [key for key, _, _ in fields]
        self.head = lines[2:end]
        self.body = "\n".join(lines[end:])
        self.sections = [title for _, title in Markdown(text).headings(2)]

        if "Status" not in self.fields:
            raise Finding(path, 3, "the template declares the `Status` field")
