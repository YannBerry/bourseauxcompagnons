from modeltranslation.translator import translator, TranslationOptions
from activities.models import Activity


class ActivityTranslationOptions(TranslationOptions):
    fields = ('name',)

translator.register(Activity, ActivityTranslationOptions)
