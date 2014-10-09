import re

class Slugify:
    """Mix-in class to provide standard slug generation abilities.

    Uses __slug__attribute__ to determine which field to use for slug generation.

    See also slugify_before_insert_listener and generate_slug.

    """
    def generate_slug(self):
        return generate_slug(getattr(self, self.__slug_attribute__))


def slugify_before_insert_listener(mapper, connection, target):
    """Event handler to auto-generate a slug on insert.

    Use this in conjunction with Slugify

    Example usage:
        event.listen(Category, 'before_insert', slugify_before_insert_listener)

    """

    if not getattr(target, target.__slug_container__):
        setattr(target, target.__slug_container__, target.generate_slug())


def generate_slug(field_value):
    """Basic slug generator - strips non-word characters and non-dashes and converts them to dashes."""
    return re.sub(r'^-|-$', '', re.sub(r'[^-\w]+', '-', field_value).lower())


