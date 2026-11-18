from .criteria import Criteria
from .finding import Finding


class Record:
    """The record a review run keeps, `spec/review/record/<date>-<mode>-<KEY>.md`
    named for the first spec of its scope, started with what a tool can
    write: the commit read, the scope, and a row for every criterion
    `review/CRITERIA.md` names. The coordinator fills in the verdict, the
    answers, and a line for each finding left open."""

    # MARK: - Initializer
    def __init__(self, specification):
        self.specification = specification

    # MARK: - Public
    def write(self, mode, keys, date):
        specs = [self.specification.require(key) for key in keys]
        criteria = Criteria(self.specification.review / "CRITERIA.md").criteria
        commit = self.specification.commit()
        directory = self.specification.review / "record"
        path = directory / f"{date}-{mode}-{specs[0].key}.md"

        if path.exists():
            raise Finding(path, 0, "is already there, and a record is written once")

        rows = "\n".join(f"| {criterion} | | |" for criterion in criteria)
        text = (
            f"# {date} {mode}\n\n"
            f"Commit `{commit}`. Scope {', '.join(spec.key for spec in specs)}. Verdict: \n\n"
            "| criterion | answer | evidence |\n|---|---|---|\n"
            f"{rows}\n"
        )

        directory.mkdir(parents=True, exist_ok=True)
        path.write_text(text, encoding="utf-8")

        return path
