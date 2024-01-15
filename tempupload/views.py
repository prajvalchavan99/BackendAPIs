from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import status
from django.utils import timezone
from django.http import HttpResponse
from django.shortcuts import get_object_or_404
from .models import *
from .serializers import UploadedFileSerializer
import os

def delete_expiered_files():
        current_time=timezone.now()
        expired_files = UploadedFile.objects.filter(expiration_time__lte=current_time)
        expired_files.update(is_deleted=True)
        for files in expired_files:
            if os.path.exists(files.file.path):
                os.remove(files.file.path)

class UploadedFileViewset(APIView):
    
    def post(self,request,*args,**kwargs):
        delete_expiered_files()

        if request.FILES.get('file'):
            uploadedfile = request.FILES['file']
            if uploadedfile.size > 52428800:
                return Response({'message':'Please upload file less than 50mb.'},status=status.HTTP_400_BAD_REQUEST)
            endpoint = request.POST.get('endpoint')
            time_validity = request.POST.get('validity')
            if UploadedFile.objects.filter(endpoint=endpoint,is_deleted=False).exists():
                print("esists")
                return Response({'message':'Endpoint already taken!'},status=status.HTTP_400_BAD_REQUEST)
            expiration_time = timezone.now() + timezone.timedelta(minutes=int(time_validity))
            file_record = UploadedFile.objects.create(file=uploadedfile,expiration_time=expiration_time,endpoint=endpoint,validity=time_validity)
            return Response({'message':'File Uploaded Successfully!'},status=status.HTTP_201_CREATED)
        else:
            return Response({'error':'Invalid Request!'},status=status.HTTP_400_BAD_REQUEST)
        
    def get(self, request, *args, **kwargs):
        delete_expiered_files()
        endpoint = self.kwargs['endpoint']
        file_data = get_object_or_404(UploadedFile, endpoint=endpoint, is_deleted=False)
        file_url = request.build_absolute_uri(file_data.file.url)
        return Response({'file_url': file_url, 'validity':file_data.validity}, status=status.HTTP_200_OK)
