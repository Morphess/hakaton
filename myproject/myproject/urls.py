from django.contrib import admin
from django.conf import settings
from django.conf.urls.static import static
from django.contrib.auth.views import LoginView, LogoutView
from django.urls import path, include
from myapp.views import upload_pdf

urlpatterns = [
    path('login/', LoginView.as_view(template_name="registration/login.html"), name='login'),
    path('admin/', admin.site.urls),
    path('logout/', LogoutView.as_view(), name="logout"),
    path('', upload_pdf, name="upload_pdf"),
    path('/', include('myapp.urls')),  # Підключення URL-ів вашого додатку
]

# Додаємо маршрут для статичних файлів
if settings.DEBUG:
    urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)
