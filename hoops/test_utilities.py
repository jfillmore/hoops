from sqlalchemy.engine import reflection
from sqlalchemy.schema import MetaData, Table, DropTable, ForeignKeyConstraint, DropConstraint


class TestUtilities(object):

    @classmethod
    def drop_tables(cls, db):
        """
        Drop All tables from database
        """
        engine = db.engine
        conn = engine.connect()

        #Only for DBz supporting transactions
        trans = conn.begin()
        inspector = reflection.Inspector.from_engine(engine)

        metadata = MetaData()

        tables = []
        all_foreign_keys = []

        for table_name in inspector.get_table_names():
            foreign_keys = []
            for foreign_key in inspector.get_foreign_keys(table_name):
                if not foreign_key.get('name'):
                    continue
                foreign_keys.append(ForeignKeyConstraint((), (), name=foreign_key['name']))
            table = Table(table_name, metadata, *foreign_keys)
            tables.append(table)
            all_foreign_keys.extend(foreign_keys)

        for foreign_key_contstraint in all_foreign_keys:
            conn.execute(DropConstraint(foreign_key_contstraint))

        for table in tables:
            conn.execute(DropTable(table))

        trans.commit()

    @classmethod
    def clear_database(cls, db):
        """
        Remove all rows from all tables
        """
        for table in reversed(db.metadata.sorted_tables):
            db.session.execute(table.delete())
        db.session.commit()
