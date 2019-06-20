from django import forms
from upload.models import File


class FileForm(forms.ModelForm):
    """A model form representing a file upload."""
    class Meta:
        model = File
        fields = ('file',)
