def random_key_generator():
    """ Method to generate random keys. It can be used to generate token, toke_secret etc.
    """
    import random
    import hashlib
    import base64

    return base64.b64encode(hashlib.sha256(str(random.getrandbits(256)))
                            .digest(), random.choice(['rA', 'aZ', 'gQ', 'hH', 'hG', 'aR', 'DD'])).rstrip('==')


def find_subclasses(cls):
    ''' Find all subclasses of class given
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
