from django.db import models
from django.contrib.auth.models import AbstractUser
# Create your models here.


class CustomUser(models.Model):

    def number():
        no = CustomUser.objects.count()
        if no == None:
            return 1
        else:
            return no + 1
    
    twilioIdentity  = models.IntegerField(default=number, unique=True)
    AuthyIdentity   = models.CharField(max_length=10, null=None)
    email           = models.TextField(blank=False)
    password        = models.TextField(blank=False)
    username        = models.TextField(blank=False)
    phoneNumber     = models.CharField(max_length=12, blank=False)
    createdAt   = models.DateTimeField(auto_now_add=True)


