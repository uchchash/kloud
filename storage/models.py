from django.db import models
from vault.utils import generate_permalink
from django.conf import settings
import datetime

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


