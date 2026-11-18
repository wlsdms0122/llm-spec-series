import re
from collections import Counter

from .finding import Finding
from .markdown import CODE_SPAN, Markdown
from .spec import KEY

WORD = re.compile(r"[\w']+")
TARGET = re.compile(r"\]\([^)]*\)")
RUN = 6
FEW = 3


class Impact:
    """Where a draft reaches the live set, found from the text alone.

    The sources are the draft and each spec it supersedes. A place is a line
    of a live document, read as if the draft were accepted, that links to a
    spec the draft supersedes, or that shares with a source a code span or a
    run of six words that few live documents write. Few is at most three
    besides the sources, so what every spec writes is not a place. Whether a
    place restates a rule or only mentions it is the review's to judge."""

    # MARK: - Initializer
    def __init__(self, specification, key):
        self.view = specification.accepting(key)
        self.draft = specification.spec(key)
        self.root = specification.root
        self.targets = [specification.spec(one) for one in self.draft.supersedes if specification.spec(one)]
        self.documents = {}

    # MARK: - Public
    def places(self):
        sources = [self.draft] + self.targets
        own = {document for source in sources for document in source.documents()}
        owners = {spec.document: spec.key for spec in self.view.live()}
        documents = [document for document in list(owners) + self.view.readmes() if document not in own]
        reasons = {}

        for document in documents:
            for line, target in self.markdown(document).links():
                for spec in self.targets:
                    if self.reaches(document, target, spec):
                        reasons.setdefault((document, line), {}).setdefault("links to", []).append(spec.key)

        spans = Counter(span for document in documents for span in set(self.spans(document)))
        runs = Counter(run for document in documents for run in set(self.runs(document)))

        for source in sources:
            rare_spans = {span for span in self.spans(source.document) if spans[span] <= FEW and not KEY.fullmatch(span.strip("`"))}
            rare_runs = {run for run in self.runs(source.document) if runs[run] <= FEW}

            for document in documents:
                for number, line in self.markdown(document).lines:
                    for span in sorted(set(CODE_SPAN.findall(line)) & rare_spans):
                        reasons.setdefault((document, number), {}).setdefault(f"shares {span}", []).append(source.key)

                    if repeated := next((run for run in self.line_runs(line) if run in rare_runs), None):
                        reasons.setdefault((document, number), {}).setdefault(f"repeats \"{' '.join(repeated)}\"", []).append(source.key)

        places = []

        for (document, line), why in sorted(reasons.items(), key=lambda item: (str(item[0][0]), item[0][1])):
            message = "; ".join(f"{reason} {', '.join(dict.fromkeys(keys))}" if reason == "links to" else f"{reason} {'with' if reason.startswith('shares') else 'from'} {', '.join(dict.fromkeys(keys))}" for reason, keys in why.items())
            places.append(Finding(document, line, message))

        return places

    # MARK: - Private
    def reaches(self, document, target, spec):
        path = target.partition("#")[0]

        if not path or re.match(r"[A-Za-z][A-Za-z0-9+.-]*:", target):
            return False

        return (document.parent / path).resolve().is_relative_to(spec.folder.resolve())

    def spans(self, document):
        return [span for _, line in self.markdown(document).spans() for span in line]

    def runs(self, document):
        return [run for _, line in self.markdown(document).lines for run in self.line_runs(line)]

    def line_runs(self, line):
        words = WORD.findall(TARGET.sub("]", line).replace("`", " ").lower())

        return [tuple(words[index:index + RUN]) for index in range(len(words) - RUN + 1)]

    def markdown(self, path):
        if path not in self.documents:
            self.documents[path] = Markdown(path.read_text(encoding="utf-8"))

        return self.documents[path]
