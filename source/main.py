import argparse
import datetime
import pathlib
import sys

from series.acceptance import Acceptance
from series.finding import Finding
from series.history import History
from series.impact import Impact
from series.lint import Lint
from series.pack import Pack
from series.record import Record
from series.release import Release
from series.scaffold import Scaffold
from series.specification import Specification

PACKAGE = pathlib.Path(__file__).resolve().parent.parent


def main():
    parser = argparse.ArgumentParser(prog="spec-series")
    commands = parser.add_subparsers(dest="command", required=True)

    init = commands.add_parser("init", help="write a series, and the specification with its first")
    init.add_argument("root", type=pathlib.Path)
    init.add_argument("--prefix", required=True)
    init.add_argument("--name", required=True)
    init.add_argument("--folder")

    draft = commands.add_parser("draft", help="start a draft under the next number of a series")
    draft.add_argument("root", type=pathlib.Path)
    draft.add_argument("title")
    draft.add_argument("--prefix")

    accept = commands.add_parser("accept", help="accept a draft that lints as accepted")
    accept.add_argument("root", type=pathlib.Path)
    accept.add_argument("key")

    release = commands.add_parser("release", help="write the release into each accepted spec that names none")
    release.add_argument("root", type=pathlib.Path)
    release.add_argument("name")

    history = commands.add_parser("history", help="where a spec stood in each tagged release")
    history.add_argument("root", type=pathlib.Path)
    history.add_argument("key")

    listing = commands.add_parser("list", help="every spec, or the live set")
    listing.add_argument("root", type=pathlib.Path)
    listing.add_argument("--live", action="store_true")
    listing.add_argument("--as", dest="accepting", metavar="KEY")

    lint = commands.add_parser("lint", help="check what the specification's rules make checkable")
    lint.add_argument("root", type=pathlib.Path)
    lint.add_argument("--as", dest="accepting", metavar="KEY")

    impact = commands.add_parser("impact", help="the live lines a draft reaches")
    impact.add_argument("root", type=pathlib.Path)
    impact.add_argument("key")

    pack = commands.add_parser("pack", help="one reviewer's reading, in one file")
    pack.add_argument("root", type=pathlib.Path)
    pack.add_argument("mode", choices=("draft", "change", "series"))
    pack.add_argument("keys", nargs="+")
    pack.add_argument("--criteria", help="the criteria groups this reviewer answers, such as ABDE")
    pack.add_argument("--attach", type=pathlib.Path, action="append", default=[])
    pack.add_argument("--report", type=pathlib.Path)
    pack.add_argument("--probes", type=pathlib.Path)
    pack.add_argument("--out", type=pathlib.Path)

    record = commands.add_parser("record", help="start a review run's record")
    record.add_argument("root", type=pathlib.Path)
    record.add_argument("mode", choices=("draft", "change", "series"))
    record.add_argument("keys", nargs="+")

    arguments = parser.parse_args()
    root = arguments.root.resolve()

    try:
        if arguments.command == "init":
            for target in Scaffold(PACKAGE / "scaffold").write(root, arguments.prefix, arguments.name, arguments.folder):
                print(f"wrote  {target.relative_to(root)}")

            return 0

        specification = Specification(root)

        if arguments.command == "draft":
            series = choose(specification, arguments.prefix)
            print(f"wrote  {Scaffold(PACKAGE / 'scaffold').draft(series, root, arguments.title).relative_to(root)}")

            return 0

        if arguments.command == "accept":
            findings, changed = Acceptance(specification).accept(arguments.key)

            for finding in findings:
                print(finding.describe(root))

            for action, path in changed:
                print(f"{action:<7} {path.relative_to(root)}")

            return 1 if findings else 0

        if arguments.command == "release":
            findings, changed = Release(specification).cut(arguments.name)

            for finding in findings:
                print(finding.describe(root))

            for action, path in changed:
                print(f"{action:<7} {path.relative_to(root)}")

            return 1 if findings else 0

        if arguments.command == "history":
            releases = History(specification).releases(arguments.key)

            for tag, state in releases:
                print(f"{tag}\t{state}")

            if not releases:
                print(f"{arguments.key} is in no tagged release")

            return 0

        if arguments.command == "list":
            return describe(specification, arguments.live, arguments.accepting, root)

        if arguments.command == "impact":
            for place in Impact(specification, arguments.key).places():
                print(place.describe(root))

            return 0

        if arguments.command == "pack":
            groups = list(arguments.criteria) if arguments.criteria else None
            text = Pack(specification).text(
                arguments.mode,
                arguments.keys,
                groups,
                [path.resolve() for path in arguments.attach],
                arguments.report,
                arguments.probes,
                specification.commit()
            )

            if arguments.out:
                arguments.out.write_text(text, encoding="utf-8")
                print(f"wrote  {arguments.out}")
            else:
                sys.stdout.write(text)

            return 0

        if arguments.command == "record":
            path = Record(specification).write(arguments.mode, arguments.keys, datetime.date.today().isoformat())
            print(f"wrote  {path.relative_to(root)}")

            return 0

        view = specification.accepting(arguments.accepting) if arguments.accepting else specification
        findings = Lint(view).findings()

        for finding in findings:
            print(finding.describe(root))

        return 1 if findings else 0
    except Finding as finding:
        print(finding.describe(root), file=sys.stderr)

        return 1


def choose(specification, prefix):
    if prefix:
        series = specification.named(prefix)

        if series is None:
            raise Finding(specification.directory, 0, f"no series has the prefix `{prefix}`")

        return series

    if len(specification.series) != 1:
        raise Finding(specification.directory, 0, f"the specification has {len(specification.series)} series, so `--prefix` names one")

    return specification.series[0]


def describe(specification, live, accepting, root):
    for finding in specification.findings:
        print(finding.describe(root), file=sys.stderr)

    view = specification.accepting(accepting) if accepting else specification
    superseders = view.superseders()

    for spec in view.live() if live else view.specs:
        by = superseders.get(spec.key)
        status = f"superseded by {', '.join(by)}" if by else spec.status
        print(f"{spec.key}\t{status}\t{spec.title}")

    return 1 if specification.findings else 0


if __name__ == "__main__":
    sys.exit(main())
