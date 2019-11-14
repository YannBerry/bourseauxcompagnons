from django.forms.widgets import ClearableFileInput, CheckboxSelectMultiple


class ImageWidget(ClearableFileInput):
	template_name = 'forms/widgets/image.html'


class GradesWidget(CheckboxSelectMultiple):
	template_name = 'forms/widgets/grades.html'
