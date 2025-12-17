from django.shortcuts import render, get_object_or_404
from django.http import JsonResponse, FileResponse
from django.views.decorators.http import require_POST
from django.contrib.auth.decorators import login_required
from django.contrib.auth import get_user_model
from .models import SharedFolder, SharedFile, FolderPermission, FilePermission
from storage.models import File, Folder
from django.urls import reverse

# Shared File View

def shared_file(request, token):
    shared_file = get_object_or_404(SharedFile, share_token=token)
    return render(request, "sharing/shared_file.html", {"file": shared_file.file})

# Shared Folder View
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

# Generate Shared File and Folder Link View

@login_required
@require_POST
def generate_shared_link(request):
    data_type = request.POST.get("type") # Get the data type from the post request
    id = request.POST.get("id") # Get the id from the post request

    if data_type == "folder": # If the data type is folder
        folder = get_object_or_404(Folder, id=id) # Get the folder object
        shared_folder = SharedFolder.objects.filter(folder=folder).first()
        if not shared_folder:
            shared_folder = SharedFolder.objects.create(folder=folder) # Create a shared folder object
        url = request.build_absolute_uri(reverse('sharing:shared_folder', args=[shared_folder.share_token])) # Build the absolute url
        return JsonResponse({'success': True, 'url': url}) # Return the success response
    elif data_type == "file": # If the data type is file
        file = get_object_or_404(File, id=id) # Get the file object
        shared_file = SharedFile.objects.filter(file=file).first()
        if not shared_file:
            shared_file = SharedFile.objects.create(file=file) # Create a shared file object
        url = request.build_absolute_uri(reverse('sharing:shared_file', args=[shared_file.share_token])) # Build the absolute url
        return JsonResponse({'success': True, 'url': url}) # Return the success response
    
    return JsonResponse({'success': False, 'error': 'Invalid type'}) # Return the error response


# Download Shared File

def download_shared_file(request, token):
    shared_file = get_object_or_404(SharedFile, share_token=token)
    file = shared_file.file
    response = FileResponse(file.file.open())
    response['Content-Disposition'] = f'attachment; filename="{file.name}"'
    return response

# Download Files From Shared Folder

def download_files_from_shared_folder(request, token):
    shared_folder = get_object_or_404(SharedFolder, share_token=token)
    file = get_object_or_404(File, id=file_id, folder=shared_folder.folder)
    response = FileResponse(file.file.open())
    response['Content-Disposition'] = f'attachment; filename="{file.name}"'
    return response

# Manage Shared Items

@login_required
def shared_items_list(request):
    shared_folders = SharedFolder.objects.filter(folder__user=request.user).order_by('-created_at')
    shared_files = SharedFile.objects.filter(file__user=request.user).order_by('-created_at')
    
    return render(request, 'sharing/manage_shared.html', {
        'shared_folders': shared_folders,
        'shared_files': shared_files

    })


# Remove Access

@login_required
@require_POST
def remove_shared_item(request):
    type = request.POST.get('type')
    id = request.POST.get('id')
    
    try:
        if type == 'folder':
            SharedFolder.objects.filter(folder__id=id, folder__user=request.user).delete()
            return JsonResponse({'success': True})
        elif type == 'file':
            SharedFile.objects.filter(file__id=id, file__user=request.user).delete()
            return JsonResponse({'success': True})
    except Exception as e:
        return JsonResponse({'success': False, 'error': str(e)})
        
    return JsonResponse({'success': False, 'error': 'Invalid type'})

# Check if shared item exists

@login_required
def get_share_info(request):
    type = request.GET.get('type')
    id = request.GET.get('id')
    
    exists = False
    url = None
    token = None
    
    if type == 'folder':
        folder = get_object_or_404(Folder, id=id, user=request.user)
        shared_folder = SharedFolder.objects.filter(folder=folder).first()
        if shared_folder:
            exists = True
            token = str(shared_folder.share_token)
            url = request.build_absolute_uri(reverse('sharing:shared_folder', args=[shared_folder.share_token]))
            
    elif type == 'file':
        file = get_object_or_404(File, id=id, user=request.user)
        shared_file = SharedFile.objects.filter(file=file).first()
        if shared_file:
            exists = True
            token = str(shared_file.share_token)
            url = request.build_absolute_uri(reverse('sharing:shared_file', args=[shared_file.share_token]))
            
    return JsonResponse({'exists': exists, 'url': url, 'token': token})

# Share with User (Email)

@login_required
@require_POST
def share_with_user(request):
    email = request.POST.get('email')
    data_type = request.POST.get('type')
    item_id = request.POST.get('id')
    
    User = get_user_model()
    
    try:
        target_user = User.objects.get(email=email)
    except User.DoesNotExist:
        return JsonResponse({'success': False, 'error': 'User not found'})
        
    if target_user == request.user:
         return JsonResponse({'success': False, 'error': 'You cannot share with yourself'})

    try:
        if data_type == 'folder':
            folder = get_object_or_404(Folder, id=item_id, user=request.user)
            # Check if permission already exists
            FolderPermission.objects.update_or_create(
                folder=folder,
                user=target_user,
                defaults={'permission': 'view'} # Default to view
            )
            return JsonResponse({'success': True})
            
        elif data_type == 'file':
            file = get_object_or_404(File, id=item_id, user=request.user)
             # Check if permission already exists
            FilePermission.objects.update_or_create(
                file=file,
                user=target_user,
                defaults={'permission': 'view'} # Default to view
            )
            return JsonResponse({'success': True})
            
    except Exception as e:
        return JsonResponse({'success': False, 'error': str(e)})

    return JsonResponse({'success': False, 'error': 'Invalid type'})

# Get Shared Users

@login_required
def get_shared_users(request):
    data_type = request.GET.get('type')
    item_id = request.GET.get('id')
    
    users_data = []
    
    if data_type == 'folder':
        folder = get_object_or_404(Folder, id=item_id, user=request.user)
        permissions = FolderPermission.objects.filter(folder=folder).select_related('user')
        for perm in permissions:
            users_data.append({
                'user_id': perm.user.id,
                'email': perm.user.email,
                'name': perm.user.get_full_name() or perm.user.username,
                'permission': perm.permission
            })
            
    elif data_type == 'file':
        file = get_object_or_404(File, id=item_id, user=request.user)
        permissions = FilePermission.objects.filter(file=file).select_related('user')
        for perm in permissions:
             users_data.append({
                'user_id': perm.user.id,
                'email': perm.user.email,
                'name': perm.user.get_full_name() or perm.user.username,
                 'permission': perm.permission
            })
    
    return JsonResponse({'success': True, 'users': users_data})

# Remove User Access

@login_required
@require_POST
def remove_user_access(request):
    data_type = request.POST.get('type')
    item_id = request.POST.get('id')
    user_id = request.POST.get('user_id')
    
    try:
        if data_type == 'folder':
            # Ensure request.user owns the folder
            folder = get_object_or_404(Folder, id=item_id, user=request.user)
            FolderPermission.objects.filter(folder=folder, user_id=user_id).delete()
            return JsonResponse({'success': True})
            
        elif data_type == 'file':
             # Ensure request.user owns the file
            file = get_object_or_404(File, id=item_id, user=request.user)
            FilePermission.objects.filter(file=file, user_id=user_id).delete()
            return JsonResponse({'success': True})
            
    except Exception as e:
        return JsonResponse({'success': False, 'error': str(e)})

    return JsonResponse({'success': False, 'error': 'Invalid type'})
