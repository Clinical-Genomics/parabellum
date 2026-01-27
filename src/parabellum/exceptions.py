class InputMismatchError(Exception):
    """Raised when the number of input files does not match the number of sample names."""

    pass


class YAMLLoadError(Exception):
    """Raised when a YAML file cannot be loaded."""

    pass


class JSONLoadError(Exception):
    """Raised when a JSON file cannot be loaded."""

    pass


class InvalidOperatorError(Exception):
    """Raised when an invalid operator is encountered in normal value processing."""

    pass


class ListOpNotSupportedError(Exception):
    """Raised when an unsupported operation is attempted on a list."""

    pass
