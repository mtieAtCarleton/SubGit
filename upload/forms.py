from django import forms
from upload.models import Submission

class SubmissionForm(forms.ModelForm):
    class Meta:
        model = Submission
        fields = ('document', )