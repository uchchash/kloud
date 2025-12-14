from django.contrib import admin
from .models import Folder

@admin.register(Folder)

class FolderAdmin(admin.ModelAdmin):
	list_display = ['name', 'parent', 'user', 'permalink', 'created_at', 'updated_at']
	list_filter = ['created_at', 'updated_at']