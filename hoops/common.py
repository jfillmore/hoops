import re
import datetime

from coaster.sqlalchemy import BaseMixin
from flask.ext.sqlalchemy import SQLAlchemy
from passlib.hash import sha512_crypt
from sqlalchemy import event


class Slugify:
    """Mix-in class to provide standard slug generation abilities.

    Uses __slug__attribute__ to determine which field to use for slug generation.

    See also slugify_before_insert_listener and generate_slug.

    """
    def generate_slug(self):
        return Slugify._generate_slug(getattr(self, self.__slug_attribute__))

    @staticmethod
    def slugify_before_insert_listener(mapper, connection, target):
        """Event handler to auto-generate a slug on insert.

        Use this in conjunction with Slugify

        Example usage:
            event.listen(Category, 'before_insert', slugify_before_insert_listener)

        """

        if not getattr(target, target.__slug_container__):
            setattr(target, target.__slug_container__, target.generate_slug())

    @staticmethod
    def _generate_slug(field_value):
        """Basic slug generator - strips non-word characters and non-dashes and converts them to dashes."""
        return re.sub(r'^-|-$', '', re.sub(r'[^-\w]+', '-', field_value).lower())


class HashedPasswordMixin:
    """Class to save password hash.

    See also hash_password_before_change_listener and generate_hash.

    """
    def generate_hash(self):
        return HashUtils.generate_hash(getattr(self, self.__hash_attribute__))

    def is_valid_password(self, password_text=None):
        if password_text:
            try:
                if getattr(self, 'enabled'):
                    return HashUtils.verify_hash(password_text, getattr(self, self.__hash_attribute__))
            except AttributeError:
                return HashUtils.verify_hash(password_text, getattr(self, self.__hash_attribute__))
        return None


class HashUtils(object):
    @staticmethod
    def hash_password_before_change_listener(mapper, connection, target):
        """Event handler to auto-generate a hash before insert.

        Use this in conjunction with HashedPasswordMixin

        Example usage:
            event.listen(AdminUser, 'before_insert', hash_password_before_change_listener)

        """
        password = getattr(target, target.__hash_attribute__)
        if (password is not None and password is not '' and not re.match(r'^\$', password)):
            setattr(target, target.__hash_attribute__, target.generate_hash())

    @staticmethod
    def generate_hash(field_value):
        """Basic hash generator"""
        return sha512_crypt.encrypt(field_value)

    @staticmethod
    def verify_hash(string_value, hash_value):
        """Verify that the passed string corressponds to the specified hash value."""
        if hash_value is None or hash_value == u'':
            return False
        return sha512_crypt.verify(string_value, hash_value)


class BareModel(object):
    """ Abstract class based which should be used to define other
    models. This will contain the common implementation details for those
    classes.
    """
    __abstract__ = True
    __table_args__ = {'mysql_engine': 'InnoDB', 'mysql_charset': 'utf8'}
    __repr_fields__ = ('id',)
    __props__ = None

    def __repr__(self):
        """
        Generic __repr__ generator that uses __repr_fields__ to build a string
        representation of the object
        """
        return "<%s (%s)>" % (
            self.__class__.__name__,
            self._get_repr_fields()
        )

    def _get_repr_fields(self):
        """Generate the fields for __repr__ strings"""
        return ' '.join(['%s=%s' % (
            field,
            getattr(self, field)
        ) for field in self.__repr_fields__])

    def to_json(self, include_subordinate=()):
        #db.session.refresh(self)
        value = self._sa_instance_state.dict
        return_value = {}
        props = value.keys()
        if self.__props__:
            props.extend(self.__props__)
        # props = props if unsafe_props is None else list(set(props) - set(unsafe_props))
        for k in props:
            if not re.match('_\w+', k):
                v = getattr(self, k)
                if type(v) == datetime.datetime:
                    v = unicode(v)
                return_value[k] = v

        for field in include_subordinate:
            return_value[field] = self._include_subordinate(field)
        return return_value

    def _include_subordinate(self, field):
        """Include a subordinate field and remove the primary referent key and jsonify recursively"""
        exclude_subordinate_column = getattr(self, field).attr.parent_token.local_remote_pairs[0][1].name

        def remove_subordinate(item):
            if exclude_subordinate_column in item:
                del item[exclude_subordinate_column]
            return item

        return [
            remove_subordinate(item.to_json())
            for item in getattr(self, field).all()
        ]

    @classmethod
    def get_one(cls, *args, **kwargs):
        """Helper to retrieve one object"""
        return cls.query.filter_by(**kwargs).one()

    @classmethod
    def get_one_or_404(cls, *args, **kwargs):
        """Helper to retrieve one object"""
        return cls.query.filter_by(**kwargs).one()


class SluggableModel(BareModel, Slugify):
    """ Model class which extends the Slugify behavior to BaseModel class. All
    models which require slug generation feature should inherit from this model.
    """
    __abstract__ = True
    __slug_container__ = "slug"

event.listen(SluggableModel, 'before_insert', Slugify.slugify_before_insert_listener, propagate=True)


class HashableModel(BareModel, HashedPasswordMixin):
    """ Model class which extends the HashedPasswordMixin behavior to BaseModel class. All
    models which require password hashing feature should inherit from this model.
    """
    __abstract__ = True

event.listen(HashableModel, 'before_insert', HashUtils.hash_password_before_change_listener, propagate=True)
event.listen(HashableModel, 'before_update', HashUtils.hash_password_before_change_listener, propagate=True)
