import os
from celery import shared_task
from django.utils import timezone
from .models import UploadedFile

UPLOAD_DIR = os.path.join('media', 'uploads')

@shared_task
def delete_expired_files_task():
    current_time = timezone.now()
    expired_files = UploadedFile.objects.filter(expiration_time__lte=current_time, is_deleted=False)
    
    for file in expired_files:
        file_path = os.path.join(UPLOAD_DIR, file.file_name)
        if os.path.exists(file_path):
            os.remove(file_path)  # Delete the file from the local filesystem

        # Mark the file as deleted in the database
        file.is_deleted = True
        file.save()
    
    return f"{expired_files.count()} expired files deleted."
