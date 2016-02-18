
Command Line Tools
==================

lymph-sqlalchemy provides a couple of lymph commands to make the workflow easiers.


``lymph init-db``
-----------------
``init-db`` command creates all tables for all models that are defined
using the library's `Base`

.. code-block:: bash

    $lymph init-db -c <config>.yml


**NOTE:**
To be able to initialize database correctly make sure that store is configured with ``models`` correctly, example:

.. code-block:: yaml

    dependencies:
        store:
            class: lymph.sqlalchemy.store:Store
            base: dhh.users.models:Base


``lymph sql-shell``
-----------------------
``sql-shell`` command would give you a shell with a `store` instance already
configured.

.. code-block:: bash

     $LYMPH_NODE_CONFIG=`pwd`/.lymph.yml lymph sql-shell -c <config>.yml
