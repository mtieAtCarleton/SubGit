from django import forms
from upload.models import Submission

# class SubmissionForm(forms.ModelForm):
#     class Meta:
#         model = Submission
#         fields = ('files', 'description')

class SubmissionForm(forms.Form):
    files = forms.FileField(widget=forms.ClearableFileInput(attrs={'multiple': True}))
