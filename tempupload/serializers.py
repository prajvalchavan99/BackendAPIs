from rest_framework import serializers
from .models import *

class UploadedFileSerializer(serializers.ModelSerializer):
    class Meta:
        model = UploadedFile
        fields = ('id' ,'file' , 'file_name', 'validity','created_at')