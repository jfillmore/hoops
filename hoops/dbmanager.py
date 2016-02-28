#!/usr/bin/env python

import logging
import os
import sys

from sqlalchemy.engine import reflection
from sqlalchemy.schema import (
    MetaData,
    Table,
    DropTable,
    ForeignKeyConstraint,
    DropConstraint
)


class DBManager(object):
    def __init__(self, db, alembic_ini_path=None):
        self.db = db
        if alembic_ini_path:
            from alembic.config import Config as AlembicConfig
            self.alembic_cfg = AlembicConfig(alembic_ini_path)
        else:
            self.alembic_cfg = None

    def recreate_db(self):
        """
        Create all the tables from database after deleting them,
        based on models implemented
        """
        self.drop_tables()
        if not self.db.metadata.tables:
            raise Exception("Database linkage error; no tables found")
        self.db.create_all()
        print "Recreated database tables: %s" % \
            (', '.join(self.db.metadata.tables.keys()))
        if self.alembic_cfg:
            from alembic.config import command
            # generate the version table, "stamping" it with the most recent rev:
            command.stamp(self.alembic_cfg, "head")

    def drop_tables(self):
        """
        Drop All tables from database

        Based on
        https://bitbucket.org/zzzeek/sqlalchemy/wiki/UsageRecipes/DropEverything

        Also removes tables outside of the current model (e.g. alembic stamp,
        tables from another branch, etc).
        """
        engine = self.db.engine
        conn = engine.connect()
        # Only for DBz supporting transactions
        trans = conn.begin()
        inspector = reflection.Inspector.from_engine(engine)
        metadata = MetaData()
        tables = []
        all_foreign_keys = []

        # gather up all foreign key constraints
        for table_name in inspector.get_table_names():
            foreign_keys = []
            for foreign_key in inspector.get_foreign_keys(table_name):
                if not foreign_key.get('name'):
                    continue
                foreign_keys.append(
                    ForeignKeyConstraint((), (), name=foreign_key['name']))
            table = Table(table_name, metadata, *foreign_keys)
            tables.append(table)
            all_foreign_keys.extend(foreign_keys)

        # strip out all foreign key constraints for easy table drops
        for foreign_key_contstraint in all_foreign_keys:
            conn.execute(DropConstraint(foreign_key_contstraint))

        # drop each table, in whatever order we please
        for table in tables:
            conn.execute(DropTable(table))
        trans.commit()
