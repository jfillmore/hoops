from passlib.hash import sha512_crypt
import re

class HashedPasswordMixin:
    """Class to save password hash.

    See also hash_password_before_change_listener and generate_hash.

    """
    def generate_hash(self):
        return generate_hash(getattr(self, self.__hash_attribute__))

    def is_valid_password(self, password_text=None):
        if password_text:
            try:
                if getattr(self, 'enabled'):
                    return verify_hash(password_text, getattr(self, self.__hash_attribute__))
            except AttributeError:
                return verify_hash(password_text, getattr(self, self.__hash_attribute__))
        return None


def hash_password_before_change_listener(mapper, connection, target):
    """Event handler to auto-generate a hash before insert.

    Use this in conjunction with HashedPasswordMixin

    Example usage:
        event.listen(AdminUser, 'before_insert', hash_password_before_change_listener)

    """
    password = getattr(target, target.__hash_attribute__)
    if (password is not None and password is not '' and
        not re.match(r'^\$', password)):
        setattr(target, target.__hash_attribute__, target.generate_hash())


def generate_hash(field_value):
    """Basic hash generator"""
    return sha512_crypt.encrypt(field_value)


def verify_hash(string_value, hash_value):
    """Verify that the passed string corressponds to the specified hash value."""
    if hash_value is None or hash_value == u'':
        return False
    return sha512_crypt.verify(string_value, hash_value)
