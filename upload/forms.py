from django import forms
from upload.models import File
from SubGit.settings import MEDIA_ROOT
import os

class FileForm(forms.ModelForm):
    class Meta:
        model = File
        fields = ('file',)

# class SubmissionForm(forms.Form):
#     files = forms.FileField(widget=forms.ClearableFileInput(attrs={'multiple': True}))
#     description = forms.CharField(max_length=255)

