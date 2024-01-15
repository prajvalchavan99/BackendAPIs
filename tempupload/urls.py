from django.urls import path
from . import views

urlpatterns = [
    path('upload/', views.UploadedFileViewset.as_view(), name='upload-file'),
    path('upload/<str:endpoint>', views.UploadedFileViewset.as_view(), name='upload-file'),
]
