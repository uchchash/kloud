from django.urls import path
from . import views

app_name = 'storage'

urlpatterns = [
    path('create_folder/', views.create_folder, name='create_folder'),
    path('upload_file/', views.upload_file, name='upload_file'),
    path('folder/<str:permalink>/', views.folder_detail, name='folder_detail'),
    path('file/<str:permalink>/', views.file_detail, name='file_detail'),
    path('folders/', views.folder_list, name='folder_list'),
    path('files/', views.file_list, name='file_list'),
    path('dashboard/', views.dashboard, name='dashboard'),
    path('edit_folder/<str:permalink>/', views.edit_folder, name='edit_folder'),
    path('delete_folder/<str:permalink>/', views.delete_folder, name='delete_folder'),
    path('delete_file/<str:permalink>/', views.delete_file, name='delete_file'),
]
