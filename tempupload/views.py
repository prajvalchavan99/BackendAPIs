import os
from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import status
from django.utils import timezone
from django.http import JsonResponse, FileResponse
from django.shortcuts import get_object_or_404
from .models import UploadedFile
from .serializers import UploadedFileSerializer
from django.conf import settings
from django.utils.timezone import now

# Directory to store uploaded files
UPLOAD_DIR = os.path.join(settings.MEDIA_ROOT, 'uploads')

os.makedirs(UPLOAD_DIR, exist_ok=True)

def delete_expired_files():
    current_time = timezone.now()
    expired_files = UploadedFile.objects.filter(expiration_time__lte=current_time, is_deleted=False)
    expired_files.update(is_deleted=True)
    for file in expired_files:
        file_path = os.path.join(UPLOAD_DIR, file.file_name)
        if os.path.exists(file_path):
            os.remove(file_path)

class UploadedFileViewset(APIView):

    def post(self, request, *args, **kwargs):
        if request.FILES.get('file'):
            uploaded_file = request.FILES['file']
            if uploaded_file.size > 52428800:  # 50MB limit
                return Response({'message': 'Please upload file less than 50mb.'}, status=status.HTTP_400_BAD_REQUEST)
            
            endpoint = request.POST.get('endpoint')
            time_validity = request.POST.get('validity')

            if UploadedFile.objects.filter(endpoint=endpoint, is_deleted=False).exists():
                return Response({'message': 'Endpoint already taken!'}, status=status.HTTP_400_BAD_REQUEST)

            expiration_time = timezone.now() + timezone.timedelta(minutes=int(time_validity))
            file_path = os.path.join(UPLOAD_DIR, uploaded_file.name)

            # Save the file locally
            with open(file_path, 'wb') as f:
                for chunk in uploaded_file.chunks():
                    f.write(chunk)

            file_record = UploadedFile.objects.create(
                file=file_path,
                file_name=uploaded_file.name,
                expiration_time=expiration_time,
                endpoint=endpoint,
                validity=time_validity
            )

            return Response({'message': 'File Uploaded Successfully!'}, status=status.HTTP_201_CREATED)
        else:
            return Response({'error': 'Invalid Request!'}, status=status.HTTP_400_BAD_REQUEST)
        
    def get(self, request, *args, **kwargs):
        endpoint = self.kwargs['endpoint']

        # Retrieve file data with expiration and deletion checks
        file_data = get_object_or_404(
            UploadedFile,
            endpoint=endpoint,
            expiration_time__gte=now(),
            is_deleted=False
        )
        serialized_data = UploadedFileSerializer(file_data).data
        return Response(serialized_data, status=status.HTTP_200_OK)

class DownloadUploadedFile(APIView):
    def get(self, request, *args, **kwargs):
        endpoint = self.kwargs['endpoint']
        file_data = get_object_or_404(
            UploadedFile,
            endpoint=endpoint,
            expiration_time__gte=now(),
            is_deleted=False
        )

        file_path = os.path.join(UPLOAD_DIR, file_data.file_name)
        if not os.path.exists(file_path):
            return JsonResponse({'error': 'File not found!'}, status=404)

        # Serve the file with metadata in headers
        response = FileResponse(open(file_path, 'rb'), content_type='application/octet-stream')
        response['Content-Disposition'] = f'attachment; filename="{file_data.file_name}"'

        return response