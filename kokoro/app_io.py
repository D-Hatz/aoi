from math import log

import gevent.monkey

gevent.monkey.patch_all()

from psycogreen.gevent import patch_psycopg

patch_psycopg()

import os
import gevent
import time
import logging
from flask import Flask
import sqlalchemy as sa

from flask_sqlalchemy import SQLAlchemy
from flask_sqlalchemy.session import Session
from sqlalchemy import event
from sqlalchemy import text
import typing as t


logging.basicConfig(
    level=logging.DEBUG, format="%(asctime)s - %(name)s - %(levelname)s - %(message)s"
)
logging.getLogger("sqlalchemy.pool").setLevel(logging.DEBUG)

logger = logging.getLogger(__name__)
logger.setLevel(logging.DEBUG)


db = SQLAlchemy()


class RouteSession(Session):
    def get_bind(
        self,
        mapper: t.Any | None = None,
        clause: t.Any | None = None,
        bind: sa.engine.Engine | sa.engine.Connection | None = None,
        **kwargs: t.Any,
    ) -> sa.engine.Engine | sa.engine.Connection:
        target_engine = self._db.engines.get(kwargs.get("target"), None)

        if target_engine:
            return target_engine

        return super().get_bind(mapper, clause, bind, **kwargs)


def setup_db_pool_logging():
    engine = db.engine

    @event.listens_for(engine, "connect")
    def on_connect(dbapi_conn, connection_record):
        print(f"[POOL] New connection created: {id(dbapi_conn)}")

    @event.listens_for(engine, "checkout")
    def on_checkout(dbapi_conn, connection_record, connection_proxy):
        print(f"[POOL] Connection checked OUT: {id(dbapi_conn)}")

    @event.listens_for(engine, "checkin")
    def on_checkin(dbapi_conn, connection_record):
        print(f"[POOL] Connection checked IN (returned): {id(dbapi_conn)}")


def inspect_session():
    """Show session and pool stats"""
    info = {
        "default_bind": str(db.session.get_bind().url),
        "session_id": id(db.session),
        "is_active": db.session.is_active,
        "pools": {},
    }

    # Show pool stats for each bind
    for bind_name, engine in db.engines.items():
        pool = engine.pool
        info["pools"][bind_name] = {
            "url": str(engine.url),
            "is_default": db.session.get_bind() is engine,
            "pool_size": pool.size(),
            "checked_out": pool.checkedout(),
            "checked_in": pool.checkedin(),
            "overflow": pool.overflow(),
        }

    return info


def create_app():
    app = Flask(__name__)

    app.config |= {
        "SQLALCHEMY_DATABASE_URI": "postgresql://postgres:postgres@localhost:5432/postgres",
        "SQLALCHEMY_BINDS": {
            "other": "postgresql://postgres:postgres@localhost:5432/other_db",
        },
        "SQLALCHEMY_ECHO": True,
        "SQLALCHEMY_ENGINE_OPTIONS": {
            "pool_size": 1,
            "max_overflow": 0,
            "pool_timeout": 30,
            "pool_recycle": 1800,
            "pool_pre_ping": True,
        },
    }

    db.init_app(app)

    with app.app_context():
        setup_db_pool_logging()

    return app


app = create_app()


@app.route("/io")
def io_bound_task():
    start_time = time.time()

    print(f"Inspect session before query: {inspect_session()}")

    stmt = text("SELECT pg_sleep(3), pg_backend_pid(), current_database()")
    result = db.session.execute(stmt, {"target": "other"}).fetchone()

    print(f"Inspect session after query: {inspect_session()}")

    pid = result[1]
    database = result[2]

    logger.debug("Query result: %s, database: %s", result, database)

    duration = time.time() - start_time

    logger.debug(
        f"[REQUEST] worker={os.getpid()} greenlet={id(gevent.getcurrent())} db_pid={pid} database={database}"
    )

    return f"I/O task completed in {round(duration, 2)} seconds on {database}\n"


