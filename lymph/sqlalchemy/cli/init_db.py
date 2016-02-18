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
            self.store.drop_all()
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
