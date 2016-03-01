from sqlalchemy.engine import reflection
from sqlalchemy.schema import (
    MetaData,
    Table,
    DropTable,
    ForeignKeyConstraint,
    DropConstraint,
)

from alembic.util import CommandError as AlembicCommandError
from lymph.cli.base import Command

from lymph.sqlalchemy.migrations import Alembic


class InitDB(Command):

    """
    Usage: lymph init-db [options]

    Creates database.

    Options:
      --clear              Drop all tables before creation

    {COMMON_OPTIONS}
    """

    def run(self):
        self.store = self.config.get_dependency('store')
        if self.args.get('--clear'):
            self.drop_everything()
        self.store.create_all()
        self.handle_migrations()

    def handle_migrations(self):
        """
        This method will check if migrations are enabled, and will stamp the
        the database with head.

        http://alembic.readthedocs.org/en/latest/cookbook.html?highlight=create_all#building-an-up-to-date-database-from-scratch
        """
        alembic = Alembic(self.store)
        if not alembic.enabled:
            return

        try:
            alembic.init()
        except AlembicCommandError:
            pass

        alembic.stamp()

    def drop_everything(self):
        """
        Recipe method for dropping all tables in case of circular constraints dependencies
        https://bitbucket.org/zzzeek/sqlalchemy/wiki/UsageRecipes/DropEverything
        """
        conn = self.store.engine.connect()

        trans = conn.begin()

        inspector = reflection.Inspector.from_engine(self.store.engine)

        # gather all data first before dropping anything.
        # some DBs lock after things have been dropped in
        # a transaction.

        metadata = MetaData()

        tbs = []
        all_fks = []

        for table_name in inspector.get_table_names():
            fks = []
            for fk in inspector.get_foreign_keys(table_name):
                if not fk['name']:
                    continue
                fks.append(ForeignKeyConstraint((),(),name=fk['name']))
            t = Table(table_name,metadata,*fks)
            tbs.append(t)
            all_fks.extend(fks)

        for fkc in all_fks:
            conn.execute(DropConstraint(fkc))

        for table in tbs:
            conn.execute(DropTable(table))

        trans.commit()

