from django.forms.widgets import ClearableFileInput


class ImageWidget(ClearableFileInput):
	template_name = 'forms/widgets/image.html'
