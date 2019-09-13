from django.db import models
from django.contrib.auth.models import AbstractUser
# Create your models here.


class CustomUser(AbstractUser):

    def number():
        no = CustomUser.objects.count()
        if no == None:
            return 1
        else:
            return no + 1
    phoneNumber = models.CharField(max_length=12, blank=False)
    twilioIdentity = models.IntegerField(default=number, unique=True)
    AuthyIdentity = models.CharField(max_length=10, null=None)
