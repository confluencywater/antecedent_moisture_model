class InvalidOrMissingTimestampException(Exception):
    "Raised when the input data file has a missing or invalid timestamp column"
    pass


class MissingDataColumnException(Exception):
    "Raised when the input data file is missing an input data column named in config"
    pass
