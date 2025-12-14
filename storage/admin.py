from django.contrib import admin
from .models import Folder, File

@admin.register(Folder)
class FolderAdmin(admin.ModelAdmin):
	list_display = ['name', 'parent', 'user', 'permalink', 'created_at', 'updated_at']
	list_filter = ['created_at', 'updated_at']


@admin.register(File)
class FileAdmin(admin.ModelAdmin):
	list_display = ['display_name', 'folder', 'user', 'created_at']
	list_filter = ['created_at', 'updated_at']