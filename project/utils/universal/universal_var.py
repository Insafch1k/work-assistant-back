from slugify import slugify

def transform_to_slug(header: str) -> str:
    return slugify(header)