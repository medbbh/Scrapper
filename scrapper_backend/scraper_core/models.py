from django.db import models
from django.conf import settings

class ScrapedData(models.Model):
    user = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE)
    url = models.URLField()
    title = models.CharField(max_length=500)
    content = models.TextField()
    images = models.JSONField(default=list)
    links = models.JSONField(default=list)
    created_at = models.DateTimeField(auto_now_add=True)
    
    class Meta:
        ordering = ['-created_at']