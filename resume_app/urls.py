from django.urls import path
from . import views

urlpatterns = [
    path('basicinfos/', views.userInfoInputPage.as_view(), name = 'basicInfos'),
    path('resume_preview/', views.ResumePreviewEditPage.as_view(), name = 'resume_preview')
]