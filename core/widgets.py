from django.contrib.gis.forms import OpenLayersWidget
from django.forms.widgets import ClearableFileInput, CheckboxSelectMultiple, CheckboxInput


# Setting the map_srid of the openlayers widget (the default widget for geometric fields) to 4326 instead of 3857
class OpenLayersWidgetSrid4326(OpenLayersWidget):
    map_srid = 4326


class ImageWidget(ClearableFileInput):
    template_name = 'forms/widgets/image.html'


class GradesWidget(CheckboxSelectMultiple):
    template_name = 'forms/widgets/grades.html'
    # class Media:
    #     css = {
    #         'all': ('css/20191113nouislider/nouislider.min.css',),
    #     }
    #     js = ('js/20191113nouislider/nouislider.min.js',)

class SelectableItemsWidget(CheckboxSelectMultiple):
    template_name = 'forms/widgets/selectable_items.html'


class ToggleSwitchWidget(CheckboxInput):
    template_name = 'forms/widgets/toggle_switch.html'
    label = None

    def get_context(self, name, value, attrs):
        context = super().get_context(name, value, attrs)
        context['widget']['label'] = self.label
        return context
