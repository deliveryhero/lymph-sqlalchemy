import unittest

from sqlalchemy.engine import create_engine
from sqlalchemy_utils.functions import create_database, database_exists, drop_database

from lymph.config import Configuration
from lymph.testing import RPCServiceTestCase
from lymph.sqlalchemy.store import Store


class ModuleSetUp():
    SAMPLE_TEST_CASE = None

    @classmethod
    def setUpModule(cls):
        cls.SAMPLE_TEST_CASE.init_db()

    @classmethod
    def tearDownModule(cls):
        cls.SAMPLE_TEST_CASE.drop_db()


class StoreTestCase(unittest.TestCase):
    USE_POSTGIS = True
    URL = 'postgresql://postgres/lymph-test-sqlalchemy'

    @classmethod
    def create_store(cls, connection=None):
        return Store(cls.URL, connection=connection)

    @classmethod
    def url(cls):
        return cls.URL

    @classmethod
    def init_db(cls):
        engine = create_engine(cls.url())
        cls.create_db(engine)
        store = cls.create_store()
        store.create_all()
        engine.dispose()

    @classmethod
    def create_db(cls, engine):
        create_database(engine.url)
        if cls.USE_POSTGIS:
            engine.execute('CREATE EXTENSION postgis;')

    @classmethod
    def drop_db(cls):
        engine = create_engine(cls.url())
        drop_database(engine.url)
        engine.dispose()

    @classmethod
    def setUpClass(cls):
        cls.create = False
        cls.engine = create_engine(cls.url())
        if not database_exists(cls.engine.url):
            cls.create_db(cls.engine)
            cls.create = True
        cls.connection = cls.engine.connect()
        cls.transaction = cls.connection.begin()
        cls.store = cls.create_store(cls.connection)
        if cls.create:
            cls.store.create_all()
        super(StoreTestCase, cls).setUpClass()

    @classmethod
    def tearDownClass(cls):
        cls.transaction.rollback()
        cls.connection.close()
        cls.engine.dispose()
        if cls.create:
            drop_database(cls.engine.url)
        super(StoreTestCase, cls).tearDownClass()

    def setUp(self):
        self.inner_transaction = self.connection.begin_nested()
        self.session = self.store.Session()
        self.session.add_all(self.get_fixtures())
        self.session.commit()
        super(StoreTestCase, self).setUp()

    def get_fixtures(self):
        return []

    def tearDown(self):
        self.session.close()
        self.inner_transaction.rollback()
        super(StoreTestCase, self).tearDown()


class StorageInterfaceTest(StoreTestCase, RPCServiceTestCase):

    service_class = None  # Define the interface here
    service_config = Configuration({
        "store": {
            "class": "lymph.sqlalchemy.store:Store",
            "uri": "postgresql://postgres/lymph-test-sqlalchemy"
        }
    })

    @classmethod
    def url(cls):
        return cls.service_config.get("store.uri")

    @classmethod
    def create_store(cls, connection=None):
        store = cls.service_config.get_instance('store')
        store.connection = connection
        return store
