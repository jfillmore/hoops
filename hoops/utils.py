import random
import hashlib
import base64
from sqlalchemy.engine import reflection
from sqlalchemy.schema import MetaData, Table, DropTable, ForeignKeyConstraint, DropConstraint

__all__ = ["Struct", "random_key_generator", "find_subclasses"]


class Struct(object):
    def __init__(self, **entries):
        self.__dict__.update(entries)


def random_key_generator():
    """ Method to generate random keys. It can be used to generate token, toke_secret etc.
    """
    return base64.b64encode(hashlib.sha256(str(random.getrandbits(256)))
                            .digest(), random.choice(['rA', 'aZ', 'gQ', 'hH', 'hG', 'aR', 'DD'])).rstrip('==')


def find_subclasses(cls):
    ''' Find all subclasses of given class
        cls - Any class whose subclass to be found
    '''
    subclasses = None
    try:
        subclasses = cls.__subclasses__()
        for d in list(subclasses):
            subclasses.extend(find_subclasses(d))
    except:
        pass
    return subclasses


class TestUtilities(object):

    @classmethod
    def drop_tables(cls, db):  # pragma: no cover
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
