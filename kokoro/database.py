import logging
import typing as t

import sqlalchemy as sa
from flask_sqlalchemy import SQLAlchemy
from flask_sqlalchemy.session import Session
from sqlalchemy.exc import UnboundExecutionError

from .sequence import FileSequence


session_sequence = FileSequence("logs/session_sequence.txt")


logging.basicConfig(
    level=logging.DEBUG, format="%(asctime)s - %(name)s - %(levelname)s - %(message)s"
)

logger = logging.getLogger(__name__)


class RouteSQLAlchemy(SQLAlchemy):
    def __init__(self, *args, **kwargs):
        """
        Initialize RouteSQLAlchemy.

        See flask_sqlalchemy.SQLAlchemy.__init__ for parameters.
        """
        super().__init__(*args, **kwargs)
        self.session.set_bind = lambda bind: self.session().set_bind(bind)
        self.session.get_engine_url = (
            lambda: self.session().get_bind().url.render_as_string(hide_password=True)
            if self.session().get_bind()
            else None
        )


class RouteSession(Session):
    def __init__(self, db: SQLAlchemy, **kwargs: t.Any) -> None:
        super().__init__(db, **kwargs)
        self.engine_bind: sa.engine.Engine | None = None
        self._unique_id = session_sequence.next()

    def __repr__(self) -> str:
        return f"<RouteSession(id={self._unique_id})>"

    def get_bind(
        self,
        mapper: t.Any | None = None,
        clause: t.Any | None = None,
        bind: sa.engine.Engine | sa.engine.Connection | None = None,
        **kwargs: t.Any,
    ) -> sa.engine.Engine | sa.engine.Connection:
        """
        Select an engine based on the ``bind_key`` of the metadata associated with
        the model or table being queried. If no bind key is set, uses the default bind.
        """

        if self.engine_bind is not None:
            return self.engine_bind

        try:
            selected_bind = super().get_bind(mapper, clause, bind, **kwargs)
        except UnboundExecutionError:
            selected_bind = None

        if selected_bind is None:
            return self._db.engines.get("default")

    def set_bind(self, bind: sa.engine.Engine | sa.engine.Connection | str):
        """Override the bind to use for this session."""
        if isinstance(bind, str):
            self.engine_bind = self._db.engines.get(bind)
        else:
            self.engine_bind = bind


db = RouteSQLAlchemy(session_options={"class_": RouteSession})
