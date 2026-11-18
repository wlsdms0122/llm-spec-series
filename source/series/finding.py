class Finding(Exception):
    """What is wrong in a series, and where."""

    # MARK: - Initializer
    def __init__(self, path, line, message):
        super().__init__(message)
        self.path = path
        self.line = line
        self.message = message

    # MARK: - Public
    def describe(self, root):
        place = self.path.relative_to(root) if self.path.is_relative_to(root) else self.path

        return f"{place}:{self.line}: {self.message}" if self.line else f"{place}: {self.message}"
