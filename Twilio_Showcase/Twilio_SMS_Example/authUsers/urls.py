from django.urls import path, re_path
from .views import (
    create_text_view,
    create_user_view,
    verify_tfa_user_view,
    send_reminder_view,
    send_tfa_user_view,
    CustomUserAPIView,
    CustomUserDetailAPIView,
)


#This is your endpoint API
urlpatterns = [
    path('sendsms/', create_text_view, name='sms'),
    #path('', index, name='index'),
    path('createuser/', create_user_view, name='view'), 
    path('authverify/', verify_tfa_user_view, name='authverify'),
    path('remind/', send_reminder_view, name='remind'),
    path('authtoken/', send_tfa_user_view, name='authtoken'),
    path('viewlist/', CustomUserAPIView.as_view(), name='viewlist'),
    re_path(r'^(?P<pk>\d+)/$', CustomUserDetailAPIView.as_view()),
    
]