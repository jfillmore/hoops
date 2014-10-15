import random
import hashlib
import base64

from .test import TestUtilities
from .model import (Slugify,
                    slugify_before_insert_listener,
                    generate_slug,
                    ActiveQuery,
                    ActiveOrSuspendedQuery,
                    NotSuspendedQuery,
                    BaseModel,
                    SluggableModel,
                    HashableModel
                    )
from .hashpass import (HashedPasswordMixin,
                       hash_password_before_change_listener,
                       generate_hash,
                       verify_hash
                       )

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
