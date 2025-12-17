from django.db import models
from vault.utils import generate_permalink
from storage.models import File, Folder
from django.conf import settings

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

# Folder Permission Model
class FolderPermission(models.Model):
    PERMISSION_CHOICES = [
        ('view', 'View'),
        ('edit', 'Edit'),
    ]
    folder = models.ForeignKey(Folder, on_delete=models.CASCADE)
    user = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE)
    permission = models.CharField(max_length=10, choices=PERMISSION_CHOICES, default='view')
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        unique_together = ('folder', 'user')
        indexes = [
            models.Index(fields=['folder', 'user']),
        ]

    def __str__(self):
        return f"{self.user.email} -> {self.folder.name} ({self.permission})"

# File Permission Model
class FilePermission(models.Model):
    PERMISSION_CHOICES = [
        ('view', 'View'),
        ('edit', 'Edit'),
    ]
    file = models.ForeignKey(File, on_delete=models.CASCADE)
    user = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE)
    permission = models.CharField(max_length=10, choices=PERMISSION_CHOICES, default='view')
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        unique_together = ('file', 'user')
        indexes = [
            models.Index(fields=['file', 'user']),
        ]

    def __str__(self):
        return f"{self.user.email} -> {self.file.name} ({self.permission})"