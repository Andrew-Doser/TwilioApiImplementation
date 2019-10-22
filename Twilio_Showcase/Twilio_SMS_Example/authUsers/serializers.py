from rest_framework import serializers
from .models import CustomUser



class CustomUserSerializer(serializers.ModelSerializer):
    class Meta:
        model = CustomUser
        fields = [
            'id',
            'phoneNumber',
            'email',
            'username',
            #'twilioIdentity',
            #'AuthyIdentity',
            'password',
        ]