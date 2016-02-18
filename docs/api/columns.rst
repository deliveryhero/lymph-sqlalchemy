.. module:: lymph.sqlalchemy.columns

lymph.sqlalchemy.columns
=========================

.. function:: AutoIncrementColumn(int_type, sequence_name=None, **kwargs)

    :param int_type: a sqlalchemy integer type
    :param sequence_name: name of the sequence used for increments

    Returns an autoincrementing integer :class:`Column <sqla:sqlalchemy.schema.Column>`. The sequence is automatically
    created and dropped when the parent table is created or dropped.
    All extra arguments are passed to the Column constructor.


.. function:: UuidColumn(*args, **kwargs)

    Returns a non-nullable :class:`Column <sqla:sqlalchemy.schema.Column>` of type UUID.
    All extra arguments are passed to the Column constructor.


.. function:: UuidPk(*args, **kwargs)

    Returns a primary key :class:`Column <sqla:sqlalchemy.schema.Column>` of type UUID. All arguments are passed to
    the sqlalchemy column constructor.
    All extra arguments are passed to the Column constructor.
