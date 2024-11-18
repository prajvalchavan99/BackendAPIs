import os
from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import status
from django.utils import timezone
from django.http import HttpResponse
from django.shortcuts import get_object_or_404
from .models import *
from .serializers import UploadedFileSerializer
from b2sdk.v2 import InMemoryAccountInfo,B2Api

info = InMemoryAccountInfo()
b2_api = B2Api(info)

application_key_id = '0052f2662b9e2150000000002'
application_key = 'K005CMr1hpopMrNUO8cz3d13hroW2sM'
bucket_name = 'backenapis'
b2_api.authorize_account('production',application_key_id,application_key)
bucket = b2_api.get_bucket_by_name(bucket_name)
def delete_expired_files():
    current_time = timezone.now()
    expired_files = UploadedFile.objects.filter(expiration_time__lte=current_time,is_deleted=False)
    expired_files.update(is_deleted=True)
    for file in expired_files:
        try:
            b2_api.delete_file_version(file_id=file.file, file_name=file.file_name)
        except Exception as e:
            print(f"Error deleting file from B2: {e}")

class UploadedFileViewset(APIView):

    def post(self, request, *args, **kwargs):
        # delete_expired_files()

        if request.FILES.get('file'):
            uploaded_file = request.FILES['file']
            if uploaded_file.size > 52428800:
                return Response({'message': 'Please upload file less than 50mb.'}, status=status.HTTP_400_BAD_REQUEST)
            endpoint = request.POST.get('endpoint')
            time_validity = request.POST.get('validity')
            if UploadedFile.objects.filter(endpoint=endpoint, is_deleted=False).exists():
                return Response({'message': 'Endpoint already taken!'}, status=status.HTTP_400_BAD_REQUEST)
            expiration_time = timezone.now() + timezone.timedelta(minutes=int(time_validity))

            bucket = b2_api.get_bucket_by_name(bucket_name)
            file_info = bucket.upload_bytes(file_name=uploaded_file.name,data_bytes=uploaded_file.read())
            file_record = UploadedFile.objects.create(
                file=file_info.id_,
                file_name=file_info.file_name,
                expiration_time=expiration_time,
                endpoint=endpoint,
                validity=time_validity
            )
            return Response({'message': 'File Uploaded Successfully!'}, status=status.HTTP_201_CREATED)
        else:
            return Response({'error': 'Invalid Request!'}, status=status.HTTP_400_BAD_REQUEST)

    def get(self, request, *args, **kwargs):
        # delete_expired_files()
        endpoint = self.kwargs['endpoint']
        file_data = get_object_or_404(UploadedFile, endpoint=endpoint, is_deleted=False)

        file_download_url = b2_api.get_download_url_for_fileid(file_id=file_data.file)
        print(file_download_url)
        file_bytes = b2_api.download_file_by_id(file_data.file)
        # file_bytes.save_to(f'uploads/{file_bytes.download_version.file_name}')

        return Response({'file_url': file_download_url, 'validity': file_data.validity}, status=status.HTTP_200_OK)
