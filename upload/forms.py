from django import forms
from upload.models import Submission

class DocumentForm(forms.ModelForm):
    class Meta:
        model = Submission
        fields = ('document', )