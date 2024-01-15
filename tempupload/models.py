from django.db import models
 
class UploadedFile(models.Model):
    file = models.FileField(upload_to='uploads/')
    created_at = models.DateTimeField(auto_now_add=True)
    validity = models.IntegerField()
    expiration_time = models.DateTimeField(null=True)
    is_deleted = models.BooleanField(default=False)
    endpoint = models.SlugField()

    def __str__(self):
        return self.file.name