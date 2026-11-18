import itertools
import subprocess

from .finding import Finding


class History:
    """Where a spec stood in each release, read from the repository's tags:
    those HEAD holds, oldest first, and the spec's head at each. A release is
    told where the spec first stands in one, and again where its status or
    what supersedes it moves."""

    # MARK: - Initializer
    def __init__(self, specification):
        self.specification = specification

    # MARK: - Public
    def releases(self, key):
        spec = self.specification.require(key)
        root = self.specification.root
        path = spec.document.relative_to(root).as_posix()
        tags = self.git("tag", "--merged", "HEAD", "--sort=creatordate")

        if tags.returncode != 0:
            raise Finding(root, 0, "a history reads the repository's tags, and this is not a git repository")

        releases = []
        last = None

        for tag in tags.stdout.split():
            shown = self.git("show", f"{tag}:{path}")
            state = self.state(shown.stdout) if shown.returncode == 0 else "absent"

            if state != last and not (last is None and state == "absent"):
                releases.append((tag, state))

            last = state

        return releases

    # MARK: - Private
    def git(self, *arguments):
        return subprocess.run(["git", "-C", str(self.specification.root), *arguments], capture_output=True, text=True)

    def state(self, text):
        head = itertools.takewhile(bool, text.split("\n")[2:])
        fields = dict(line.partition(": ")[::2] for line in head)
        by = fields.get("Superseded-By")

        return f"superseded by {by}" if by else fields.get("Status", "")
