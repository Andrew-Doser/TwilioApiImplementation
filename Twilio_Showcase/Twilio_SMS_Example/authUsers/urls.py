from django.urls import path, re_path
from .views import (
    send_verify_view,
    verify_text_view,
    CustomUserAPIView,
    create_email_view,
)

app_name='authUsers' #Needed to run tests

#This is your endpoint API
urlpatterns = [
    path('sendsms/', send_verify_view, name='sms'),
    path('sendemail/', create_email_view, name='email'),
    path('viewlist/', CustomUserAPIView.as_view(), name='viewlist'),
    path('verifysms/', verify_text_view, name='smsverify'),

    
]