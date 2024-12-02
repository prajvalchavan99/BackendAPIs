from django.db import models
 
class UploadedFile(models.Model):
    file = models.CharField(max_length=200,null=True)
    file_name = models.CharField(max_length=200,null=True)
    created_at = models.DateTimeField(auto_now_add=True,null=True)
    validity = models.IntegerField(null=True)
    expiration_time = models.DateTimeField(null=True)
    is_deleted = models.BooleanField(default=False)
    endpoint = models.SlugField(null=True)

    def __str__(self):
        return self.file_name