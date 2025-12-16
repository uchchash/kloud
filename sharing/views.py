from django.shortcuts import render, get_object_or_404
from django.http import JsonResponse, FileResponse
from django.views.decorators.http import require_POST
from django.contrib.auth.decorators import login_required
from .models import SharedFolder, SharedFile
from storage.models import File, Folder
from django.urls import reverse

# Shared File View

@login_required
def shared_file(request, token):
    shared_file = get_object_or_404(SharedFile, share_token=token)
    return render(request, "sharing/shared_file.html", {"file": shared_file.file})

# Shared Folder View
@login_required
def shared_folder(request, token, subfolder_permalink=None):
    shared_folder_instance = get_object_or_404(SharedFolder, share_token=token)
    root_folder = shared_folder_instance.folder
    current_folder = root_folder
    if subfolder_permalink:
        current_folder = get_object_or_404(Folder, permalink=subfolder_permalink)
        temp_folder = current_folder
        is_descendant = False
        while temp_folder:
            if temp == root_folder:
                is_descendant = True
                break
            temp_folder = temp_folder.parent
        if not is_descendant:
            return get_object_or_404(Folder, id=-1)
    return render(request, "sharing/shared_folder.html", {
        "folder": current_folder,
        "token": token,
        "is_root": current_folder == root_folder
    })    

