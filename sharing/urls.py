from django.urls import path
from . import views

app_name = 'sharing'

urlpatterns = [
    path('file/<str:token>/', views.shared_file, name='shared_file'),
    path('folder/<str:token>/', views.shared_folder, name='shared_folder'),
    path('generate_link/', views.generate_shared_link, name='generate_shared_link'),
    path('file/<str:token>/download/', views.download_shared_file, name='download_shared_file'),
    path('folder/<str:token>/download/<int:file_id>/', views.download_files_from_shared_folder, name='download_file_from_shared_folder'),
    path('manage/', views.shared_items_list, name='manage_shared_items'),
    path('revoked/', views.remove_shared_item, name='revoke_shared_item'),
    path('get-info/', views.get_share_info, name='get_share_info'),
    path('share-with-user/', views.share_with_user, name='share_with_user'),
    path('get-shared-users/', views.get_shared_users, name='get_shared_users'),
    path('remove-user-access/', views.remove_user_access, name='remove_user_access'),
]