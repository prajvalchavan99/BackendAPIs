from django.urls import path
from . import views

urlpatterns = [
    path('upload/', views.UploadedFileViewset.as_view(), name='upload-file'),
    path('upload/<str:endpoint>', views.UploadedFileViewset.as_view(), name='upload-file'),
    path('download-uploaded-file/<str:endpoint>', views.DownloadUploadedFile.as_view(), name='download-uploaded-file'),
]
