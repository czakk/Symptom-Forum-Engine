from django.contrib.auth.models import User
from django.db import models

# Create your models here.

class Profile(models.Model):
    user = models.OneToOneField(User,
                                related_name='profile',
                                on_delete=models.CASCADE)
    birthday = models.DateField(blank=True,
                                null=True)
    photo = models.ImageField(upload_to='users/%Y/%m/%d/',
                              blank=True)

    def __str__(self):
        return f'{self.user.username} profile'