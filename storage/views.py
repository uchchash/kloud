from django.shortcuts import redirect, render, get_object_or_404
from django.contrib.auth.decorators import login_required
from .forms import FolderForm, FileForm
from .models import Folder, File
from payment.models import UserSubscription
from django.http import FileResponse
from rest_framework import viewsets, permissions
from .serializers import FileSerializer, FolderSerializer


@login_required
def create_folder(request):
    parent_permalink = request.GET.get('parent')
    parent_folder = None
    
    if parent_permalink:
        parent_folder = get_object_or_404(Folder, permalink=parent_permalink, user=request.user)
    
    if request.method == "POST":
        name = request.POST.get('name')
        parent_id = request.POST.get('parent')
        
        folder = Folder(name=name, user=request.user)
        if parent_id:
            folder.parent = get_object_or_404(Folder, permalink=parent_id, user=request.user)
        folder.save()
        
        if folder.parent:
            return redirect('vault:folder', permalink=folder.parent.permalink)
        return redirect('vault:dashboard')
    
    return render(request, 'storage/create_folder.html', {'parent_folder': parent_folder})

@login_required
def rename_folder(request, permalink):
    folder = get_object_or_404(Folder, permalink=permalink, user=request.user)
    if request.method == "POST":
        new_name = request.POST.get('name')
        if new_name:
            folder.name = new_name
            folder.save()
    
    if folder.parent:
        return redirect('vault:folder', permalink=folder.parent.permalink)
    return redirect('vault:dashboard')

@login_required
def delete_folder(request, permalink):
    folder = get_object_or_404(Folder, permalink=permalink, user=request.user)
    parent_permalink = folder.parent.permalink if folder.parent else None
    folder.delete()
    
    if parent_permalink:
        return redirect('vault:folder', permalink=parent_permalink)
    return redirect('vault:dashboard')

@login_required
def upload_file(request):
    folder_id = request.POST.get('folder') or request.GET.get('folder')
    parent_folder = None
    
    if folder_id:
        parent_folder = get_object_or_404(Folder, id=folder_id, user=request.user)
    
    if request.method == "POST":
        uploaded_file = request.FILES.get('file')
        if uploaded_file:
            file_instance = File(
                user=request.user,
                file=uploaded_file,
                folder=parent_folder
            )
            file_instance.save()
            
            if parent_folder:
                return redirect('vault:folder', permalink=parent_folder.permalink)
            return redirect('vault:dashboard')
    
    return render(request, 'storage/upload_file.html', {'parent_folder': parent_folder})

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
    file_instance = get_object_or_404(File, permalink=permalink, user=request.user)
    return render(request, 'storage/file_detail.html', {'file': file_instance})


@login_required
def rename_file(request, permalink):
    file_instance = get_object_or_404(File, permalink=permalink, user=request.user)
    if request.method == "POST":
        new_name = request.POST.get('name')
        if new_name:
            file_instance.display_name = new_name
            file_instance.save()
            
    if file_instance.folder:
        return redirect('vault:folder', permalink=file_instance.folder.permalink)
    return redirect('vault:dashboard')

@login_required
def delete_file(request, permalink):
    file_instance = get_object_or_404(File, permalink=permalink, user=request.user)
    parent_permalink = file_instance.folder.permalink if file_instance.folder else None
    file_instance.delete()
    
    if parent_permalink:
        return redirect('vault:folder', permalink=parent_permalink)
    return redirect('vault:dashboard')

@login_required
def download_file(request, permalink):
    file_instance = get_object_or_404(File, permalink=permalink, user=request.user)
    response = FileResponse(file_instance.file)
    response['Content-Disposition'] = f'attachment; filename="{file_instance.display_name or file_instance.file.name}"'
    return response


@login_required
def folder_list(request):
    folders = Folder.objects.filter(user=request.user)
    return render(request, 'storage/folder_list.html', {'folders': folders})

@login_required
def file_list(request): 
    files = File.objects.filter(user=request.user)
    return render(request, 'storage/file_list.html', {'files': files})


def dashboard(request):
    subscriptions = UserSubscription.objects.filter(user=1)
    return render(request, 'storage/dashboard.html', {'subscriptions': subscriptions})


class FileViewSet(viewsets.ModelViewSet):
    queryset = File.objects.all()
    serializer_class = FileSerializer
    permission_classes = [permissions.IsAuthenticated]

    def get_queryset(self):
        return File.objects.filter(user=self.request.user)


    def perform_create(self, serializer):
        serializer.save(user=self.request.user)

class FolderViewSet(viewsets.ModelViewSet):
    queryset = Folder.objects.all()
    serializer_class = FolderSerializer
    permission_classes = [permissions.IsAuthenticated]

    def get_queryset(self):
        return Folder.objects.filter(user=self.request.user)

    def perform_create(self, serializer):
        serializer.save(user=self.request.user)
