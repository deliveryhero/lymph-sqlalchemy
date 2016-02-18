# -*- coding: utf-8 -*-

from __future__ import print_function

from alembic.util import CommandError as AlembicCommandError

from lymph.cli.base import Command
from lymph.sqlalchemy.migrations import Alembic


class MigrationCommand(Command):
    """
    Usage: lymph sql-migrations <command> [<revision> ...] [options]

    Description:
        Runs alembic using the lymph storage configuration

    Commands:
        upgrade <revision>         Upgrade to the specified revision
        downgrade <revision>       Downgrade to the specified revision
        revision                   Create a new revision
        init                       Initialize a new store
        current                    Show the current revision (of the database)
        history                    Show history of the current revision
        branches                   Show branch points in the history
        heads                      Show available heads
        merge <revision> ...       Create a merging revision from specified parents
        stamp <revision>           Stamp the database to contain the specified revision
    Options:
        --sql                      Only output the SQL, don't execute the queries
        --message=<msg>, -m <msg>  Message string to use with 'revision'
        --autogenerate, --auto     Populate revision script with candidate migration
                                   operations, based on comparison of database to model.
        --verbose                  Report more information
    {COMMON_OPTIONS}
    """

    short_description = 'Migrate databases'

    command_args_mapper = {
        'upgrade': {
            '<revision>': 'revisions',
        },
        'downgrade': {
            '<revision>': 'revisions',
        },
        'revision': {
            '--message': 'message',
            '--auto': 'auto',
        },
        'merge': {
            '--message': 'message',
            '<revision>': 'revisions',
        },
        'stamp': {
            '<revision>': 'revisions',
        },
        'history': {
            '--verbose': 'verbose',
        },
        'current': {
            '--verbose': 'verbose',
        },
        'branches': {
            '--verbose': 'verbose',
        },
        'heads': {
            '--verbose': 'verbose',
        },
        'init': {},
    }

    def get_command_args(self, command_name):
        args = {}
        for key, value in self.command_args_mapper[command_name].items():
            try:
                args[value] = self.args[key]
            except KeyError:
                pass
        return args

    def run(self):
        command_name = self.args.get('<command>')
        offline = self.args.get('--sql')
        store = self.config.get_dependency('store')
        alembic = Alembic(store, offline=offline)

        try:
            getattr(alembic, command_name)(**self.get_command_args(command_name))
        except AlembicCommandError as e:
            print(str(e))
            return 1
        except AttributeError as e:
            print('Command not supported %s' % command_name)
            return 1
        else:
            return 0
