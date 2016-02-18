========================
Migrations
========================

lymph-sqlalchemy provides an optional support for migrations using the alembic
library. It provides a command line interface which provides shortcuts to the
alembic commands.

The CLI essentially wraps
https://alembic.readthedocs.org/en/latest/index.html


sql-migrate
===============

To enable migrations for your models, you need to provide a migration path in
the config file. The migration path is the path under where your migration
versions would live. Here is an example config.

.. code:: yaml

    dependencies:
        store:
            ...
            migrations:
                path: dhh.restaurants

    interfaces:
        restaurants:
            ...


.. note::

    If you don't provide the ``migrations`` block under the ``store`` block in the
    config of lymph, the migrations will not be enabled.

You can also use auto increment intergers instead of hashes for your migration
versions by providing a ``numerical_revisions`` option to the ``migrations``
block.


.. code:: yaml

    dependencies:
        store:
            ...
            migrations:
                path: dhh.restaurants
                numerical_revisions: True

    interfaces:
        restaurants:
            ...


First Migration
---------------

After enabling the migrations, you should call the ``init-db`` command to call
the sqlalchemy `create_all
<http://docs.sqlalchemy.org/en/latest/core/metadata.html#sqlalchemy.schema.MetaData.create_all>`_
method and then followed by the alembic `init
<http://alembic.readthedocs.org/en/latest/api/commands.html>`_ method.

.. code:: bash

    $ lymph init-db -c conf/storage.yml --clear

This command will clear your tables, create new tables. This command will then
create the migration directory for you, followed by stamping the current
version as the head.

This workflow is in accordance to:

http://alembic.readthedocs.org/en/latest/cookbook.html?highlight=create_all#building-an-up-to-date-database-from-scratch


Usage
-----

Whenever there is a schema change, the developer needs to create a migration
script.

The easiest way to do this is by using ``--auto`` of the ``revision``
command e.g.:

.. code:: bash

    $ lymph sql-migrations revision --auto --message "<msg here>" -c conf/storage.yml

The command above will inspect the status of the schema as defined by the code and compare it with
the database. From there it will generate a Python script under ``migrations/versions/`` that will handle
the migration itself.

To migrate the database forward to the most recent revision we run:

.. code:: bash

    $ lymph sql-migrations upgrade -c conf/storage.yml

To migrate until a specific revision run:

.. code:: bash

    $ lymph sql-migrations upgrade 0011 -c conf/storage.yml

To roll back run:

.. code:: bash

    $ lymph sql-migrations downgrade 0010 -c conf/storage.yml


If you want to see list of all migrations run:

.. code:: bash

    $ lymph sql-migrations history -c conf/storage.yml

To know current state of database run:

.. code:: bash

    $ lymph sql-migrations current -c conf/storage.yml


sql-migrate upgrade
-----------------------

Upgrade the database to the specified revision.

.. code:: bash

    $ lymph sql-migrations upgrade [<revision>] -c conf/storage.yml

If no revision is given, upgrades to include all current heads,
otherwise applies all migrations necessary to reach the given revision.

Note that revisions can be specified using unique prefixes. If there
is only one ``0015_*``, then just supply ``0015``.

sql-migrate downgrade
-------------------------

Downgrade the database to the specified revision.

.. code:: bash

    $ lymph sql-migrations downgrade <revision> -c conf/storage.yml


sql-migrate revision
------------------------

Create a new revision.

.. code:: bash

    $ lymph sql-migrations revision [--auto] --message='<message>' -c conf/storage.yml

This creates a new (template of a) migration script in ``migrations/versions``. If using
``--auto`` this will be pre-filled with the schema changes which could automatically be detected.

sql-migrate current
-----------------------

Shows the current revision of the database.


sql-migrate heads
-----------------------

Shows the head revisions in the migrations repository.


sql-migrate history
-----------------------

Shows the history of the current head(s).


sql-migrate branches
------------------------

Shows the revisions where history branches.


sql-migrate merge
---------------------

Merge specified revisions (or specify ``heads`` to merge all heads) into a new revision.

In an ideal world, all migrations would form a linear sequence of database changes.
If however, two people introduce migrations at the same time, it might happen that they
both base their migration on the same database state. In that case the migrations directory
has multiple head revisions.

.. code:: bash

    $ lymph sql-migrations heads -c conf/storage.yml
    0019_changes_by_john (head)
    0019_changes_by_jane (head)

Often these changes will be entirely independent, sometimes they will need some reconciliation.
To create a new migration which contains this reconciliation (or just the information that no
further commands are necessary to merge these changes), do

.. code:: bash

    $ lymph sql-migrations merge heads --message='Merging from John and Jane' -c conf/storage.yml

Afterwards:

.. code:: bash

    $ lymph sql-migrations heads -c conf/storage.yml
    0020_merging_from_john_and_jane


sql-migrate stamp
---------------------

Overwrite the database to pretend to be a specific revision.

.. warning::

   Unless you indeed want to overwrite the `alembic_version` table, this is not the command you want.
