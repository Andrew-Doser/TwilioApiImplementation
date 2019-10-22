from django.shortcuts import render
from django.views.decorators.csrf import csrf_exempt

from twilio.rest import Client

from django.http import HttpResponse, JsonResponse
from django.shortcuts import get_object_or_404
from .models import CustomUser
import json

from sendgrid import SendGridAPIClient
from sendgrid.helpers.mail import Mail

from authy.api import AuthyApiClient
from .serializers import CustomUserSerializer
from rest_framework import viewsets, mixins, generics
from rest_framework.parsers import JSONParser

"""
    This file contains 3 different views and 1 class:
        Views:
            send_verify_view,
            verify_text_view,
            create_email_view,
        
        Class:
            CustomUserAPIView,
"""


"""
Shown below is the sid and token related to just the SMS
service
"""
sms_account_sid = 'ACb53c21c66369986927aebdd947dd9a63'
auth_token = 'f4933378853ee8825db447e1d20b3eea'
smsClient = Client(sms_account_sid, auth_token) #here is the client from Twilio Package


"""
Below is where the sendGrid Client is created
"""
sendGrid = SendGridAPIClient('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')

"""
Twilio Verification API KEY is shown below
"""

twilioVerify_sid = 'VA18abdc7c4bde1d587aec7936910af87b'





    
@csrf_exempt
def send_verify_view(request):
    """
    Purpose:
        Take data from the HTTP Request Post to
        send a text message to target user.
    Fields:
        data            =>  holds data from HTTP Request Post
        verification    =>  holds data on the verify created
    CreatedBy:
        Andrew Doser
        9/11/2019
    UpdatedLast:
        10/3/2019
    """
    passed_id = request.POST.get('id', False)
    obj = None
    if passed_id is not False:
        obj = CustomUser.objects.filter(id=passed_id).first()
    else:
        return HttpResponse(status=400)
    
    verification = smsClient.verify \
                     .services(twilioVerify_sid) \
                     .verifications \
                     .create(to=('+1' + getattr(obj, 'phoneNumber')), channel='sms')
    return HttpResponse(verification.status)




@csrf_exempt
def verify_text_view(request):
    """
    Purpose:
        Take data from the HTTP Request POST to
        verify code sent to user
    Fields:
        data     =>  holds data from HTTP Request Post
            sms  =>  holds phone number for user
            code =>  holds verification code
        message  =>  holds data on the message created
    CreatedBy:
        Andrew Doser
        9/23/2019
    """

    passed_id = request.POST.get('id', False)
    passed_code = request.POST.get('code', False)
    obj = None
    if passed_id is not False:
        obj = CustomUser.objects.filter(id=passed_id).first()
    else:
        return HttpResponse(status=400)

    # 'id' should be the target user id
    # verifyClient.verify.services().verification_checks.create()
    # Verifies a code sent to a specific phone number
    # it returns a json object with information on if the verify passes
    verification = smsClient.verify \
                     .services(twilioVerify_sid) \
                     .verification_checks \
                     .create(to=('+1' + getattr(obj, 'phoneNumber')), code=passed_code)




    #if 'approved' in verification.status:
    message = smsClient.messages \
            .create(
                body="Thanks for verifying your Phone Number! Your all set for text reminders!",
                from_='+15205954045',
                to=('+1' + getattr(obj, 'phoneNumber')),
            )
    return HttpResponse(str(verification))


@csrf_exempt
def create_email_view(request):
    """
    Purpose:
        Take data from the HTTP Request Post to
        send an email to target user.
    Fields:
        data    =>  holds data from HTTP Request Post
        message =>  holds data on the message created
    CreatedBy:
        Andrew Doser
        9/11/2019
    UpdatedLast:
        10/3/2019
    """
    # if request.method != "POST":
    #     return HttpResponse(status=404)
    passed_id = request.POST.get('id', False)
    obj = None
    if passed_id is not False:
        obj = CustomUser.objects.filter(id=passed_id).first()
    else:
        return HttpResponse(status=400)
    
    message = Mail(
        from_email='from_email@example.com',
        to_emails=getattr(obj, 'email'),
        subject='Sending with Twilio SendGrid is Fun',
        html_content='<strong>and easy to do anywhere, even with Python</strong>')
    try:
        response = sendGrid.send(message)
        return HttpResponse(response.body)
    except Exception as e:
        return HttpResponse(e.message)



def is_json(json_data):
    """
    Purpose:
        Needed a function to validate json function.
        Probably could have done it with a serializer.
    Created By:
        Andrew Doser
        10/3/2019
    """
    try:
        real_json = json.loads(json_data)
        is_valid = True
    except ValueError:
        is_valid = False
    return is_valid

class CustomUserAPIView(
    mixins.CreateModelMixin,
    mixins.UpdateModelMixin,
    mixins.DestroyModelMixin,
    mixins.RetrieveModelMixin, 
    generics.ListAPIView):

    """
    Purpose:
        This was created in order to view users that was
        created and edit their data.
    Created By:
        Andrew Doser
        9/26/2019
    """
    permission_classes = []
    authentication_classes = []
    serializer_class = CustomUserSerializer
    passed_id = None
    def get_queryset(self):
        qs = CustomUser.objects.all()
        query = self.request.GET.get('q')
        if query is not None:
            qs = qs.filter(email__icontains=query)
        return qs
    def get_object(self):
        request = self.request
        passed_id = request.GET.get('id') or self.passed_id
        print(passed_id)
        queryset = self.get_queryset()
        obj = None
        if passed_id is not None:
            obj = get_object_or_404(queryset, id=passed_id)
            self.check_object_permissions(request, obj)
        return obj
    def perform_destroy(self, instance):
        if instance is not None:
            return instance.delete()
        return None

    def get(self, request, *args, **kwargs):
        #print("test")
        url_passed_id   = request.GET.get('id')
        json_data       = {}
        body_           = request.body
        if is_json(body_):
            json_data   = json.loads(request.body)

        new_passed_id   = json_data.get('id', None)
        #print(request.body)
        passed_id       = url_passed_id or new_passed_id or None
        self.passed_id = passed_id
        if passed_id is not None:
            return self.retrieve(request, *args, **kwargs)
        return super().get(request, *args, **kwargs)

    def post(self, request, *args, **kwargs):
        return self.create(request, *args, **kwargs)

    def put(self, request, *args, **kwargs):
        url_passed_id   = request.GET.get('id')
        print(url_passed_id)
        json_data       = {}
        body_           = request.body
        if is_json(body_):
            json_data   = json.loads(request.body)

        new_passed_id   = json_data.get('id', None)
        #print(request.body)
        passed_id       = url_passed_id or new_passed_id or None
        self.passed_id = passed_id
        return self.update(request, *args, **kwargs)
    def patch(self, request, *args, **kwargs):
        url_passed_id   = request.GET.get('id')
        json_data       = {}
        body_           = request.body
        if is_json(body_):
            json_data   = json.loads(request.body)

        new_passed_id   = json_data.get('id', None)
        #print(request.body)
        passed_id       = url_passed_id or new_passed_id or None
        self.passed_id = passed_id
        return self.update(request, *args, **kwargs)
    def delete(self, request, *args, **kwargs):
        url_passed_id   = request.GET.get('id')
        json_data       = {}
        body_           = request.body
        if is_json(body_):
            json_data   = json.loads(request.body)

        new_passed_id   = json_data.get('id', None)
        #print(request.body)
        passed_id       = url_passed_id or new_passed_id or None
        self.passed_id = passed_id
        return self.destroy(request, *args, **kwargs)


