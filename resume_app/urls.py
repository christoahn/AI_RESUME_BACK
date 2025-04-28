from django.urls import path
from . import views

urlpatterns = [
    path('basicinfos/', views.second_page.as_view(), name = 'basicInfos'),
    path('resume_preview/', views.third_page.as_view(), name = 'resume_preview')
]