from django.db import models

from user.models import User


# Create your models here.
class Issue(models.Model):
    user = models.OneToOneField(User, on_delete=models.PROTECT, null=True)
    location = models.CharField(max_length=50)
    key = models.CharField(max_length=25, null=True)
    value = models.CharField(max_length=100, null=True)
    message = models.TextField(null=True)
    critical = models.BooleanField()
    is_customer_project = models.BooleanField()
    time = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f'{self.location} || {self.time}'
