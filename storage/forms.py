from django import forms
from .models import Folder, File

class FolderForm(forms.ModelForm):
    class Meta:
        model = Folder
        fields = ['name', 'parent']

class FileForm(forms.ModelForm):
    class Meta:
        model = File
        fields = ['file', 'folder'] 