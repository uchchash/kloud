from django.db import models
from vault.utils import generate_permalink,random_upload_path
from django.conf import settings
import datetime
import os

"""
Models for the storage application.
Users can create folder and upload files into those folders.
"""


class Folder(models.Model):
	user = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE, related_name='folders')
	name = models.CharField(max_length=100, null=True, blank=False)
	parent = models.ForeignKey('self', on_delete=models.CASCADE, null=True, blank=True, related_name='children')
	permalink = models.CharField(max_length=20, default=generate_permalink, unique=True, editable=False)
	created_at = models.DateTimeField(auto_now_add=True)
	updated_at = models.DateTimeField(auto_now=True)

	class Meta:
		ordering = ['name']
		indexes = [
		    models.Index(fields=['user', 'parent']),
            models.Index(fields=['permalink']),
		]
	def __str__(self):
		return f"{self.name} by ({self.user.email})"

	def get_full_path(self):
		if self.parent:
			return f"{self.parent.get_full_path()}/{self.name}"
		return self.name

class File(models.Model):
	user = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE, related_name='files')
	file = models.FileField(upload_to=random_upload_path)
	display_name = models.CharField(max_length=200, null=True, blank=True)
	folder = models.ForeignKey(Folder, on_delete=models.CASCADE, related_name='files', null=True, blank=True)
	permalink = models.CharField(max_length=25, unique=True, default=generate_permalink, editable=False)
	created_at = models.DateTimeField(auto_now_add=True)
	updated_at = models.DateTimeField(auto_now=True)

	class Meta:
		indexes = [
			models.Index(fields=['user', 'folder']),
			models.Index(fields=['permalink'])
		]
	def save(self, *args, **kwargs):
		if not self.display_name and self.file:
			self.display_name = os.path.basename(self.file.name)
		super().save(*args, **kwargs)
	
	def __str__(self):
		return f"{self.display_name} by {self.user}"

