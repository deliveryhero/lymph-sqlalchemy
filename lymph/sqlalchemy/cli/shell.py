from lymph.cli.shell import ShellCommand

from lymph.sqlalchemy.base import Base


class SqlShell(ShellCommand):

    """
    Usage: lymph sql-shell [options]

    Creates database.

    Notes:
        Env variable LYMPH_NODE_CONFIG=.lymph.yml should be specified

    Description:
        Opens a Python shell with instance of Store.

    {COMMON_OPTIONS}
    """

    def get_imported_objects(self, **kwargs):
        imported_objects = super(SqlShell, self).get_imported_objects(**kwargs)

        store = self.config.get_dependency('store')
        imported_objects['store'] = store
        imported_objects['Base'] = store.Base

        return imported_objects
