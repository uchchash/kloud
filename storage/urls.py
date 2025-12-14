from django.urls import path
from . import views

app_name = 'storage'

urlpatterns = [
    path('create_folder/', views.create_folder, name='create_folder'),
    path('upload_file/', views.upload_file, name='upload_file'),
    path('folder/<str:permalink>/', views.folder_detail, name='folder_detail'),
    path('file/<str:permalink>/', views.file_detail, name='file_detail'),
]
