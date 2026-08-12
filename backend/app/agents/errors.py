class SourceUnavailableError(Exception):
    """Raised when the source is down or times out."""
    pass

class RateLimitError(Exception):
    """Raised when the source rate limits us."""
    pass

class MalformedResponseError(Exception):
    """Raised when the source returns invalid data (e.g., HTML instead of JSON)."""
    pass

class SchemaDriftError(Exception):
    """Raised when the source schema has changed unexpectedly."""
    pass
