
from sqlalchemy.exc import SQLAlchemyError


def _helper(method, instance, db):
    try:
        getattr(db.session, method)(instance)
        db.session.commit()
    except SQLAlchemyError:
        db.session.rollback()
        raise
    return instance


def add(instance, db):
    return _helper('add', instance, db)


def delete(instance, db):
    return _helper('delete', instance, db)


def update(instance, db, **changes):
    """
    This update helper uses add -- SQLAlchemy will figure it out in most cases
    Use db.session.merge() for more complicated situations.
    See the SQLAlchemy manual.
    """
    if changes:
        for key, value in changes.items():
            setattr(instance, key, value)
    return _helper('add', instance, db)
