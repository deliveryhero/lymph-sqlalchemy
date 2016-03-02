# -*- encoding: utf8 -*-

from setuptools import setup, find_packages

with open('README.rst') as f:
    description = f.read()


setup(
    name='lymph-sqlalchemy',
    version='0.7.0',
    url='http://github.com/deliveryhero/lymph-sqlalchemy/',
    packages=find_packages(),
    namespace_packages=['lymph'],
    author=u'© Delivery Hero Holding GmbH',
    license=u'Apache License (2.0)',
    maintainer=u'Dushyant Rijhwani',
    maintainer_email=u'dushyant.rijhwani@deliveryhero.com',
    long_description=description,
    include_package_data=True,
    install_requires=[
        'lymph>=0.1.0',
        'SQLAlchemy>=1.0.9',
        'psycopg2>=2.6.1',
        'SQLAlchemy-Utils>=0.31.4',
        'alembic>=0.8.2',
    ],
    entry_points={
        'lymph.cli': [
            'init-db = lymph.sqlalchemy.cli.init_db:InitDB',
            'sql-shell = lymph.sqlalchemy.cli.shell:SqlShell',
            'sql-migrations = lymph.sqlalchemy.cli.migrate:MigrationCommand',
        ],
    }
)
