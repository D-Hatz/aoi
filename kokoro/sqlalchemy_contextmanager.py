from contextlib import contextmanager
from .database import db


@contextmanager
def query_comment(comment: str):
    """
    Context manager to add comment to all queries within block.

    WARNING: Only use string literals - no f-strings or .format().

    Usage:
        with query_comment("loading orders"):
            orders = db.session.execute(text("SELECT ..."))
    """
    session = db.session()
    session.info["comment"] = comment
    try:
        yield
    finally:
        session.info.pop("comment", None)
