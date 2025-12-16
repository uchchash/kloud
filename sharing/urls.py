from django.urls import path
from . import views

app_name = 'sharing'

urlpatterns = [
    path('file/<str:token>/', views.shared_file, name='shared_file'),
    path('folder/<str:token>/', views.shared_folder, name='shared_folder'),
    path('generate_link/', views.generate_shared_link, name='generate_shared_link'),
]