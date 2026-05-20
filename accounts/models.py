from django.db import models
from django.contrib.auth.models import User

class UsageTracking(models.Model):
    user = models.OneToOneField(User, on_delete=models.CASCADE)
    summariser_uses = models.IntegerField(default=0)
    sentiment_uses = models.IntegerField(default=0)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    def __str__(self):
        return f"{self.user.username} - Usage"
    
    class Meta:
        verbose_name = "Usage Tracking"