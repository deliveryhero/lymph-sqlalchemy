from sqlalchemy import Column, Integer, String
import sqlalchemy

import lymph

from lymph.sqlalchemy.interfaces import StoreInterface
from lymph.sqlalchemy.testing import StorageInterfaceTest
from lymph.sqlalchemy.base import Base


class User(Base):
     __tablename__ = 'users'

     id = Column(Integer, primary_key=True)
     name = Column(String)


class MyInterface(StoreInterface):

    @lymph.rpc()
    def is_healthy(self):
        try:
            self.store.engine.execute('SELECT 1')
        except sqlalchemy.exc.OperationalError:
            return False
        return True

    @lymph.rpc()
    def create_user(self):
        with self.store.get_session() as session:
            user = User(name='Me')
            session.add(user)
            session.flush()
            id = user.id
        return id

    @lymph.rpc()
    def get_user(self, pk):
        with self.store.get_session() as session:
            user = session.query(User).filter(User.id == pk).one()
            response = {
                'name': user.name,
                'id': user.id
            }

        return response


class TestStorageInterface(StorageInterfaceTest):

    service_class = MyInterface

    def test_is_healthy(self):
        self.assertTrue(self.client.is_healthy())

    def test_create_user(self):
        id = self.client.create_user()
        self.assertTrue(id)
        user = self.client.get_user(pk=id)
        self.assertEqual(user['id'], id)
