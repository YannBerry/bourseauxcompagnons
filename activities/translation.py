from modeltranslation.translator import translator, TranslationOptions
from activities.models import Activity, Grade


class ActivityTranslationOptions(TranslationOptions):
    fields = ('name',)

translator.register(Activity, ActivityTranslationOptions)


class GradeTranslationOptions(TranslationOptions):
    fields = ('name',)

translator.register(Grade, GradeTranslationOptions)
