from django.db import models
from vault.utils import generate_permalink
from storage.models import File, Folder

# Create Shared Folder Model

class SharedFolder(models.Model):
    folder = models.ForeignKey(Folder, on_delete=models.CASCADE)
    share_token = models.CharField(max_length=20, default=generate_permalink, unique=True, editable=False)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    def __str__(self):
        return f"{self.folder.name} by {self.folder.user}"
    
    class Meta:
        indexes = [
            models.Index(fields=['folder', 'share_token']),
        ]

# Create Shared File Model

class SharedFile(models.Model):
    file = models.ForeignKey(File, on_delete=models.CASCADE)
    share_token = models.CharField(max_length=20, default=generate_permalink, unique=True, editable=False)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    def __str__(self):
        return f"{self.file.name} by {self.file.user}"

    class Meta:
        indexes = [
            models.Index(fields=['file', 'share_token']),
        ]