from django.contrib import admin
from django.urls import path, include
from django.conf import settings
from django.conf.urls.static import static
from django.views.generic import TemplateView

urlpatterns = [
    path('admin/', admin.site.urls),
    path('test-404/', TemplateView.as_view(template_name='404.html'), name='test_404'),
    path('vault/', include('vault.urls')),
    path('', include('storage.urls')),
    path('payment/', include('payment.urls')),
    path('sharing/', include('sharing.urls')),
]


if settings.DEBUG:
    urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)
    urlpatterns += static(settings.STATIC_URL, document_root=settings.STATIC_ROOT)
