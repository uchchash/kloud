from django.shortcuts import redirect, render
from django.contrib.auth.decorators import login_required
from .forms import FolderForm, FileForm
from .models import Folder, File

@login_required
def create_folder(request):
    if request.method == "POST":
        form = FolderForm(request.POST)
        if form.is_valid():
            folder = form.save(commit=False)
            folder.user = request.user
            folder.save()
            return redirect('storage:folder_detail', permalink=folder.permalink)
    else:
        form = FolderForm()
    return render(request, 'storage/create_folder.html', {'form': form})

@login_required
def upload_file(request):
    if request.method == "POST":
        form = FileForm(request.POST, request.FILES)
        if form.is_valid():
            file_instance = form.save(commit=False)
            file_instance.user = request.user
            file_instance.save()
            return redirect('storage:file_detail', permalink=file_instance.permalink)
    else:
        form = FileForm()
    return render(request, 'storage/upload_file.html', {'form': form})

@login_required
def folder_detail(request, permalink):
    folder = Folder.objects.get(permalink=permalink, user=request.user)
    files = folder.files.all()
    subfolders = folder.children.all()
    return render(request, 'storage/folder_detail.html', {
        'folder': folder,
        'files': files,
        'subfolders': subfolders
    })  

@login_required
def file_detail(request, permalink):
    file_instance = File.objects.get(permalink=permalink, user=request.user)
    return render(request, 'storage/file_detail.html', {'file': file_instance})