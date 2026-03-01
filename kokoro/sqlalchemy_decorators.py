"""
SQLAlchemy route decorators.

Provides decorators for controlling database behavior in Flask routes.
"""

from functools import wraps

from .database import db
from .sqlalchemy_contextmanager import query_comment


def set_route_bind(bind_name: str):
    """
    Decorator to route all database queries in a request to a specific bind.

    Sets the session's engine_bind before the route executes, and restores
    the original bind after completion (even if an exception occurs).

    Args:
        bind_name: Name of the bind (must exist in SQLALCHEMY_BINDS)

    Usage:
        @app.route("/read")
        @set_route_bind("replica")
        def read_data():
            return db.session.execute(text("SELECT ...")).fetchall()

    Note:
        Decorator order matters - @set_route_bind must come AFTER @app.route
    """

    def decorator(func):
        @wraps(func)
        def wrapper(*args, **kwargs):
            original_bind = db.session.get_bind()
            db.session.set_bind(bind_name)
            try:
                return func(*args, **kwargs)
            finally:
                db.session.set_bind(original_bind)

        return wrapper

    return decorator


def with_query_comment(comment: str):
    """
    Decorator to add comment to all queries in a route.

    WARNING: Only use string literals - no f-strings or .format().

    Usage:
         @app.route("/users")
         @set_route_bind("replica")
         @with_query_comment("endpoint=/users readonly=true")
         def get_users():
             return db.session.execute(text("SELECT * FROM users")).fetchall()


    Note:
        Decorator order matters - @with_query_comment should come AFTER @app.route
    """

    def decorator(func):
        @wraps(func)
        def wrapper(*args, **kwargs):
            with query_comment(comment):
                return func(*args, **kwargs)

        return wrapper

    return decorator
