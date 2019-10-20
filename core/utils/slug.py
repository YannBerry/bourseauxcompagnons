from django.utils.text import slugify


def unique_slug_generator(model_instance, reference_field_value):
    '''
    Create a unique slug based on the reference field indicated in parameters.
    Format : {reference_field value}-{incremental number if reference_field value already exists}
    '''
    slug = slugify(reference_field_value)
    unique_slug = slug
    nb = 1
    model_class = model_instance.__class__
    while model_class._default_manager.filter(slug=unique_slug).exists():
        nb += 1
        unique_slug = f'{slug}-{nb}'
    return unique_slug