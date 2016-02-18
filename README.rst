lymph-sqlalchemy
================

This is a library is a basic wrapper around sqlalchemy that provides an easy
way to write an interface, integrate logging and helps in testing.

Store
-----

The ``lymph.sqlalchemy.store.Store`` class is a basic wrapper around sqlalchemy,
it configures the engine and gives an interface to sessions.


.. code-block:: python

    from lymph.sqlalchemy.store import Store
    store = Store('postgresql://postgres/lymph-test-sqlalchemy')
    # Access the engine
    engine = store.engine
    engine.execute('SELECT 1')

    # The sessions are context managers
    with store.get_session() as session:
        session.add(user)


You can pass all of the engine args to the ``Store``, they would be passed on
when creating the engine.


Defining Models
--------------

The recommended way of defining your models is by first creating an sqlalchemy declarative base class and then
define your models like any normal sqlalchemy models:

.. code-block:: python

    from sqlalchemy import Column, Integer, String
    from sqlalchemy.ext.declarative import declarative_base

    Base = declarative_base()

    class User(Base):
         __tablename__ = 'users'

         id = Column(Integer, primary_key=True)
         name = Column(String)


**IMPORTANT**: Please put the ``Base`` class in the same python module as the models, else you may
have some import problems.

Interface
---------

The ``lymph.sqlalchemy.interface.StoreInterface`` class uses the the lymph config to
configure a store instance.

An example config for a ``StoreInterface`` looks like this, it has a dependency
on store.

.. code-block:: python

    import lymph
    from lymph.sqlalchemy.interface import StoreInterface

    class UserInterface(StoreInterface):

        @lymph.rpc()
        def create_user(self, data):
            user = User(**data)
            with self.store.get_session() as session:
                session.add(user)


.. code-block:: yaml

    dependencies:
        store:
            class: lymph.sqlalchemy.store:Store
            uri: postgresql://postgres/users
            pool_size: 5
            max_overflow: 10
            pool_timeout: 30
            base: dhh.users.models:Base

    interfaces:
        restaurants:
            class: UserInterface
            store: dep:store

Testing
-------

The library provides a ``lymph.sqlalchemy.testing.StorageInterfaceTest`` to help
you write your unittests. You would extend this class by providing it your own
database config and your service interface.

The class would create the database on ``setupClass`` and it would create the
tables and the models that you provided as fixtures in ``setUp`` method of the
test case.

In the ``teardown`` this class would drop all the tables.

.. code-block:: python

    from lymph.sqlalchemy.testing import StorageInterfaceTest


    class UserInterfaceTest(StorageInterfaceTest):

        def get_fixtures(self):
            self.user = User(name='Test')
            self.user_2 = User(name='Test 2')
            return [self.user, self.user_2]

        def test_get_user(self):
            user = self.client.get(pk=self.user.id)
            user_2 = self.client.get(pk=self.user_2.id)
            self.assertEqual(user.id, self.user.id)
            self.assertEqual(user_2.id, self.user_2.id)


Command Line Interfaces
-----------------------

This library provides a couple of cli to make the workflow easiers.


``init-db`` command would create all the tables for all models that are defined
using the library's `Base`

.. code-block:: bash

    $lymph init-db -c <config>.yml


.. code-block:: yaml

    dependencies:
        store:
              class: lymph.sqlalchemy.store:Store
              base: dhh.users.models:Base


``sql-shell`` command would give you a shell with a `store` instance already
configured.

.. code-block:: bash

     $LYMPH_NODE_CONFIG=`pwd`/.lymph.yml lymph sql-shell -c <config>.yml
