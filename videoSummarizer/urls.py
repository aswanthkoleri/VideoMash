
from django.contrib import admin
from django.urls import path,include
from django.conf import settings
from django.contrib.staticfiles.urls import staticfiles_urlpatterns
from django.conf.urls.static import static
from . import views

urlpatterns = [
    path('admin/', admin.site.urls),
    path('',views.index),
    path('main/',include('main.urls')),
    path('subSummarize',include('subSummarize.urls'))
]
urlpatterns+=staticfiles_urlpatterns()
if settings.DEBUG:
    urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)
