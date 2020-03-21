from functools import partial
from itertools import groupby
from operator import attrgetter

from django import forms
from django.forms.models import ModelChoiceIterator, ModelChoiceField, ModelMultipleChoiceField

class CustomForm(forms.Form):
    # def __init__(self, *args, **kwargs):
    #     kwargs.setdefault('label_suffix', '')  
    #     super(CustomForm, self).__init__(*args, **kwargs)

    def get_form(self, request, obj=None, **kwargs):
        form = super(BaseAdmin, self).get_form(request, obj, **kwargs)
        for field in form.base_fields:
            if form.base_fields.get(field).required:
                form.base_fields.get(field).label_suffix = " *"
        return form

class CustomModelForm(forms.ModelForm):
    # def __init__(self, *args, **kwargs):
    #     kwargs.setdefault('label_suffix', '')  
    #     super(CustomForm, self).__init__(*args, **kwargs)

    def get_form(self, request, obj=None, **kwargs):
        form = super(BaseAdmin, self).get_form(request, obj, **kwargs)
        for field in form.base_fields:
            if form.base_fields.get(field).required:
                form.base_fields.get(field).label_suffix = " *"
        return form

class GroupedModelChoiceIterator(ModelChoiceIterator):
    '''
    Redefining ModelChoiceIterator to add the possibility to group the choices by a choosen attribute of the model.
    This allow to feed the optgroups defined in the optgroups context attribute (defined in django/forms/widgets.py).

    -> append the belonging group to each choice in the form of a tuple.
    '''
    def __init__(self, field, groupby):
        self.groupby = groupby
        super().__init__(field)

    def __iter__(self):
        if self.field.empty_label is not None:
            yield ("", self.field.empty_label)
        queryset = self.queryset
        # Can't use iterator() when queryset uses prefetch_related()
        if not queryset._prefetch_related_lookups:
            queryset = queryset.iterator()
        for group, objs in groupby(queryset, self.groupby):
            yield (group, [self.choice(obj) for obj in objs])


class GroupedModelChoiceField(ModelChoiceField):
    '''
    Redefining ModelChoiceField to add the possibility to group the choices by a choosen attribute of the model.
    This allow to feed the optgroups defined in the optgroups context attribute defined in django/forms/widgets.py.

    -> Add the 'choices_groupby' attribute to ModelChoiceField.
    '''
    def __init__(self, *args, choices_groupby, **kwargs):
        if isinstance(choices_groupby, str):
            choices_groupby = attrgetter(choices_groupby)
        elif not callable(choices_groupby):
            raise TypeError('choices_groupby must either be a str or a callable accepting a single argument')
        self.iterator = partial(GroupedModelChoiceIterator, groupby=choices_groupby)
        super().__init__(*args, **kwargs)


class GroupedModelMultipleChoiceField(ModelMultipleChoiceField, GroupedModelChoiceField):
    '''
    Redefining ModelChoiceField to add the possibility to group the choices by a choosen attribute of the model.
    This allow to feed the optgroups defined in the optgroups context attribute defined in django/forms/widgets.py.

    -> Just pass the choices_groupby argument to GroupedModelChoiceField
    '''
    pass

    # def __init__(self, *args, choices_groupby, **kwargs):
    #     self.choices_groupby = choices_groupby
    #     super().__init__(*args, choices_groupby= choices_groupby, **kwargs)

    # def __init__(self, *args, choices_groupby, **kwargs):
    #     if isinstance(choices_groupby, str):
    #         choices_groupby = attrgetter(choices_groupby)
    #     elif not callable(choices_groupby):
    #         raise TypeError('choices_groupby must either be a str or a callable accepting a single argument')
    #     self.iterator = partial(GroupedModelChoiceIterator, groupby=choices_groupby)
    #     super().__init__(*args, **kwargs)