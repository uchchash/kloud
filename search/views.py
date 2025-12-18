from django.shortcuts import render
from django.contrib.auth.decorators import login_required
from django.contrib.postgres.search import SearchVector, SearchRank, SearchQuery
from django.db.models import Q
from storage.models import File, Folder
from sharing.models import FilePermission, FolderPermission


@login_required
def search_view(request):
    """
    Full-text search for files and folders.
    Returns results for items the user owns or has been shared with them.
    """
    query = request.GET.get('q', '').strip()
    files = File.objects.none()
    folders = Folder.objects.none()
    
    if query:
        search_query = SearchQuery(query)
        
        # Search folders user owns or has permission to
        folder_vector = SearchVector('name')
        user_folder_ids = Folder.objects.filter(user=request.user).values_list('id', flat=True)
        shared_folder_ids = FolderPermission.objects.filter(user=request.user).values_list('folder_id', flat=True)
        
        folders = Folder.objects.filter(
            Q(id__in=user_folder_ids) | Q(id__in=shared_folder_ids)
        ).annotate(
            search=folder_vector,
            rank=SearchRank(folder_vector, search_query)
        ).filter(
            Q(search=search_query) | Q(name__icontains=query)
        ).order_by('-rank', 'name')
        
        # Search files user owns or has permission to
        file_vector = SearchVector('display_name')
        user_file_ids = File.objects.filter(user=request.user).values_list('id', flat=True)
        shared_file_ids = FilePermission.objects.filter(user=request.user).values_list('file_id', flat=True)
        
        files = File.objects.filter(
            Q(id__in=user_file_ids) | Q(id__in=shared_file_ids)
        ).annotate(
            search=file_vector,
            rank=SearchRank(file_vector, search_query)
        ).filter(
            Q(search=search_query) | Q(display_name__icontains=query)
        ).order_by('-rank', 'display_name')
    
    return render(request, 'search/results.html', {
        'query': query,
        'files': files,
        'folders': folders,
    })
