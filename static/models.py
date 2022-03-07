from django.db import models


# Create your models here.
class HomepageImage(models.Model):
    image = models.ImageField(upload_to='source/')
    active = models.BooleanField(default=True)

    def __str__(self):
        return f'{self.image}'
