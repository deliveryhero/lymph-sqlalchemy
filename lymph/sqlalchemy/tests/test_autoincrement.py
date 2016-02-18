from sqlalchemy import Column, Integer, String
import lymph

from lymph.sqlalchemy.interfaces import StoreInterface
from lymph.sqlalchemy.testing import StoreTestCase
from lymph.sqlalchemy.base import Base
from lymph.sqlalchemy.columns import UuidPk, AutoIncrementColumn
from lymph.sqlalchemy.store import Store


class User(Base):
     __tablename__ = 'xusers'

     id = UuidPk()
     int_id = AutoIncrementColumn(Integer, sequence_name='user_int_id_seq')
     name = Column(String)


class AutoIncrementTestCase(StoreTestCase):
    def test_increment(self):
        a = User(name='a')
        b = User(name='b')
        with self.store.get_session() as session:
            session.add(a)
            session.add(b)
            session.commit()
            self.assertEqual(a.int_id, 1)
            self.assertEqual(b.int_id, 2)
