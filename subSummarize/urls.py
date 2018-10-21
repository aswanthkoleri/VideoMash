from django.urls import path
from . import views

app_name= 'subSummarize'
urlpatterns = [
    path('',views.main),
]
