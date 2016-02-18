import uuid

import sqlalchemy
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy import Column, Sequence
from sqlalchemy.schema import CreateSequence, DropSequence


def UuidColumn(*args, **kwargs):
    kwargs.setdefault('nullable', False)
    kwargs['type_'] = UUID(as_uuid=True)
    return Column(*args, **kwargs)


def UuidPk(*args, **kwargs):
    kwargs.setdefault('default', uuid.uuid4)
    kwargs['primary_key'] = True
    return UuidColumn(*args, **kwargs)


def AutoIncrementColumn(type_, **kwargs):
    try:
        sequence_name = kwargs.pop('sequence_name')
    except KeyError:
        raise TypeError('AutoIncrementColumn needs a `sequence_name`')
    kwargs.update(
        server_default=sqlalchemy.text("nextval('%s')" % sequence_name),
        nullable=False,
        unique=True,
    )
    col = Column(type_, **kwargs)

    def after_parent_attach(target, parent):
        sequence = Sequence(sequence_name)
        sqlalchemy.event.listen(col.table, 'before_create', CreateSequence(sequence))
        sqlalchemy.event.listen(col.table, 'after_drop', DropSequence(sequence))

    sqlalchemy.event.listen(col, 'after_parent_attach', after_parent_attach)
    return col

