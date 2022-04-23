from django.utils.translation import gettext_lazy as _

class Translatable(object):
    """
    A class that allows a lazy string to translate that contains variables to be transported
    in the parameters of a function and to load the translation later in the function definition
    by applying str() on the class instance.
    If the lazy string has no variable, then it doesn't need this class. Indeed there is no .format
    that will force it to be translated immediatly.
    """
    def __init__(self, text, context):
        self.text = text
        self.context = context

    def __str__(self):
        return _(self.text).format(**self.context)