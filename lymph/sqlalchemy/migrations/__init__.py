
from __future__ import print_function
import os
import re
import pkg_resources

from alembic.script import ScriptDirectory
from alembic.config import Config
from alembic import command
from alembic.util import CommandError as AlembicCommandError



class AlembicConfig(Config):

    def get_template_directory(self):
        return pkg_resources.resource_filename('lymph.sqlalchemy', 'migrations/templates')


class Alembic(object):

    exclude_tables = {'spatial_ref_sys'}

    def __init__(self, store, offline=False):
        self.store = store
        self.offline = offline
        self.enabled = True if self.store.migrations else False
        self.numerical_revisions = self.store.migrations.get('numerical_revisions', False)

        self._config = None

        def run_env(script):
            if self.offline:
                self._run_migrations_offline()
            else:
                self._run_migrations_online()

        ScriptDirectory.run_env = run_env

    @property
    def config(self):
        if not self._config:
            self._config = AlembicConfig()

            package_name = self.store.migrations.get('path')
            migrations_directory = 'migrations'
            script_location = pkg_resources.resource_filename(package_name, migrations_directory)
            self._config.set_main_option('script_location', script_location)

        return self._config

    def _al_include_object(self, object, name, type_, reflected, compare_to):
        if type_ == 'table':
            return name not in self.exclude_tables

        return True

    def _run_migrations_online(self):
        from alembic import context

        context.configure(
            connection=self.store.engine,
            target_metadata=self.store.Base.metadata,
            include_object=self._al_include_object,
        )
        with context.begin_transaction():
            context.run_migrations()

    def _run_migrations_offline(self):
        from alembic import context

        filename = "%s.sql" % self.store.engine.name
        print('Generating SQL script: %s', filename)
        with open(filename, 'w') as f:
            context.configure(
                url=self.store.engine.url,
                output_buffer=f,
                target_metadata=self.store.Base.metadata,
                include_object=self._al_include_object,
            )
            with context.begin_transaction():
                context.run_migrations()

    def generate_revision_id(self):
        if not self.numerical_revisions:
            return None
        def extract_number(rev_id):
            match = re.match(r"\d+", rev_id)
            if not match:
                raise AlembicCommandError('Wrong revision id {}'.format(rev_id))
            return int(match.group(0))
        directory = ScriptDirectory.from_config(self.config)
        current_revision_numbers = [extract_number(head) for head in directory.get_heads()] or [0]
        new_revision_number = max(current_revision_numbers) + 1
        return "{:0>4}".format(new_revision_number)

    def init(self, script_location=None):
        try:
            import geoalchemy2
        except ImportError:
            template = 'generic'
        else:
            template = 'geoalchemy'


        # PS: This config file is just a workaround, it is not needed. We
        # just use it to initialize the config. Changes done to this file
        # will not be reflected.
        script_location = self.config.get_main_option('script_location')
        config_file = os.path.join(script_location, 'alembic.ini')
        self.config.config_file_name = config_file
        directory = script_location or self.config.get_main_option('script_location')
        command.init(self.config, directory=directory, template=template)

    def upgrade(self, revisions=None):
        revisions = revisions or ['head']
        if len(revisions) != 1:
            msg = ('Only supply a single revision for upgrade')
            raise AlembicCommandError(msg)

        command.upgrade(self.config, revisions[0], sql=self.offline)

    def downgrade(self, revisions=None):
        revisions = revisions or ['head']
        if len(revisions) != 1:
            msg = ('Only supply a single revision for downgrade')
            raise AlembicCommandError(msg)

        command.downgrade(self.config, revisions[0], sql=self.offline)

    def revision(self, message=None, auto=None):
        auto = auto or False
        if not message:
            raise AlembicCommandError('Please provide a message')
        revision_id = self.generate_revision_id()
        command.revision(self.config, message=message,
                         autogenerate=auto, sql=self.offline,
                         rev_id=revision_id)

    def merge(self, message=None, revisions=None):
        if not message:
            raise AlembicCommandError('Please provide a message')
        revision_id = self.generate_revision_id()
        command.merge(self.config, message=message, revisions=revisions, rev_id=revision_id)

    def stamp(self, revisions=None):
        revisions = revisions or ['head']
        if len(revisions) != 1:
            msg = ('Only supply a single revision for upgrade')
            raise AlembicCommandError(msg)

        command.stamp(self.config, revisions[0], sql=self.offline)

    def history(self, verbose=None):
        command.history(self.config, verbose=verbose)

    def current(self, verbose=None):
        command.current(self.config, verbose=verbose)

    def branches(self, verbose=None):
        command.branches(self.config, verbose=verbose)

    def heads(self, verbose=None):
        command.heads(self.config, verbose=verbose)
