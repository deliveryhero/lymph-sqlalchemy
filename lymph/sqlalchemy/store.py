from contextlib import contextmanager
import logging
import time
import warnings

import sqlalchemy
from sqlalchemy.orm import sessionmaker, scoped_session

from lymph.utils import import_object
from lymph.sqlalchemy.base import Base


logger = logging.getLogger(__name__)
sql_logger = logger.getChild('sql')


@sqlalchemy.event.listens_for(sqlalchemy.engine.Engine, "before_cursor_execute", retval=True)
def before_cursor_execute(conn, cursor, statement, parameters, context, executemany):
    conn.info.setdefault('query_start_time', []).append(time.time())
    return statement, parameters


@sqlalchemy.event.listens_for(sqlalchemy.engine.Engine, "after_cursor_execute")
def after_cursor_execute(conn, cursor, statement, parameters, context, executemany):
    total = time.time() - conn.info['query_start_time'].pop(-1)
    sql_logger.info("%s ## params=%r duration=%s", statement, parameters, total)


@sqlalchemy.event.listens_for(sqlalchemy.pool.Pool, "checkout")
def ping_connection(conn, record, proxy):
    cursor = conn.cursor()
    try:
        cursor.execute("SELECT 1")
    except Exception as ex:
        logger.warning('failed to ping connection %r: %s', conn, ex)
        raise sqlalchemy.exc.DisconnectionError()
    cursor.close()


class Store(object):

    def __init__(self, uri, base=Base, migrations=None, **kwargs):
        if 'models' in kwargs:
            warnings.warn("models argument was removed", DeprecationWarning)

        timezone = kwargs.pop('timezone', 'utc')
        connect_args = kwargs.pop('connect_args', {})
        options = connect_args.get('options', '')
        options = '%s -c timezone=%s' % (options, timezone)
        connect_args.update({
            'options': options
        })

        if isinstance(base, basestring):
            base = import_object(base)

        self.Base = base
        self.migrations = migrations or {}
        self._connection = kwargs.pop('connection', None)
        self.engine = sqlalchemy.create_engine(uri, connect_args=connect_args, **kwargs)
        self.init_session()

    @property
    def connection(self):
        return self._connection

    @connection.setter
    def connection(self, connection):
        self._connection = connection
        self.init_session()

    def init_session(self):
        self.Session = scoped_session(sessionmaker(bind=self.connectable,
                                                   expire_on_commit=False))

    @property
    def connectable(self):
        return self.connection or self.engine

    @contextmanager
    def get_session(self):
        session = self.Session()
        try:
            yield session
            session.commit()
        except:
            session.rollback()
            raise
        finally:
            session.close()

    def create_all(self):
        return self.Base.metadata.create_all(self.connectable)

    def drop_all(self):
        return self.Base.metadata.drop_all(self.connectable)
