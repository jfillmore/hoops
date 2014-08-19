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
