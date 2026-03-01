"""
SQLAlchemy utility functions.

Provides inspection and debugging utilities for sessions and pools.
"""

from flask_sqlalchemy import SQLAlchemy


def inspect_session(db: SQLAlchemy) -> dict:
    """
    Get session and pool statistics.
    
    Returns information about the current session and all connection pools.
    Useful for debugging connection issues and monitoring pool usage.
    
    Args:
        db: The SQLAlchemy instance to inspect
    
    Returns:
        dict with:
            - default_bind: URL of current bind
            - session_sequence_id: Unique session ID
            - session_id: Python object ID
            - is_active: Whether session has active transaction
            - pools: Dict of pool stats per bind
    
    Usage:
        info = inspect_session(db)
        return jsonify(info)
    """
    session = db.session()
    info = {
        "default_bind": str(session.get_bind().url),
        "session_sequence_id": session._unique_id,
        "session_id": id(session),
        "is_active": session.is_active,
        "pools": {},
    }

    for bind_name, engine in db.engines.items():
        key = bind_name if bind_name is not None else "primary"
        pool = engine.pool
        info["pools"][key] = {
            "url": str(engine.url),
            "is_current": session.get_bind() is engine,
            "pool_size": pool.size(),
            "checked_out": pool.checkedout(),
            "checked_in": pool.checkedin(),
            "overflow": pool.overflow(),
        }

    return info
