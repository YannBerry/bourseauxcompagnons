from django.forms.widgets import ClearableFileInput, CheckboxSelectMultiple, CheckboxInput


class ImageWidget(ClearableFileInput):
    template_name = 'forms/widgets/image.html'


class GradesWidget(CheckboxSelectMultiple):
    template_name = 'forms/widgets/grades.html'


class SelectableItemsWidget(CheckboxSelectMultiple):
    template_name = 'forms/widgets/selectable_items.html'


class ToggleSwitchWidget(CheckboxInput):
    template_name = 'forms/widgets/toggle_switch.html'
    label = None

    def get_context(self, name, value, attrs):
        context = super().get_context(name, value, attrs)
        context['widget']['label'] = self.label
        return context