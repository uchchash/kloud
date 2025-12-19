from django.urls import path
from django.urls import path, include
from rest_framework.routers import DefaultRouter
from vault.views import UserListViewSet, UserMeViewSet
from storage.views import FileViewSet, FolderViewSet

router = DefaultRouter()
router.register(r'files', FileViewSet, basename='file')
router.register(r'folders', FolderViewSet, basename='folder')
router.register(r'users', UserListViewSet, basename='user')
router.register(r'user/me', UserMeViewSet, basename='me')

urlpatterns = [
    path('', include(router.urls)),
]