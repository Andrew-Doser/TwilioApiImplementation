from django.shortcuts import render
from django.views.decorators.csrf import csrf_exempt
from twilio.rest import Client
from django.http import HttpResponse
from .models import CustomUser
from authy.api import AuthyApiClient
from .serializers import CustomUserSerializer
from rest_framework import viewsets, mixins, generics


"""
    This file contains 5 different views:

    create_text_view,
    create_user_view,
    verify_tfa_user_view,
    send_reminder_view,
    send_tfa_user_view,
"""


"""
Shown below is the sid and token related to just the SMS
service
"""
sms_account_sid = 'ACb53c21c66369986927aebdd947dd9a63'
auth_token = 'f4933378853ee8825db447e1d20b3eea'
smsClient = Client(sms_account_sid, auth_token) #here is the client from Twilio Package



"""
Shown below is the sid, token, and service sid for Notify
service in Twilio
"""
twilioNotifyService = 'IS7e4922bc6fe17cdbe48d9c8bcae3f4fc'
notify_account_sid = 'ACb42ffdc680522e56ca36182e61126f7d'
notify_auth_token = '9430ad36c97707e43f741d9ad294975b'

notifyClient = Client(notify_account_sid, notify_auth_token) #here is the client from Twilio Package





"""
Twilio API Key for Authy is shown below
This key is required for Two-Factor Authentication
"""
AUTHY_API_KEY = 'Z1nU706FBlc77bUqREQp5YdJDEIVy3fe'
authy_api = AuthyApiClient(AUTHY_API_KEY)





# Create your views here.
@csrf_exempt
def create_user_view(request):

    """
    Purpose:
        Take data from the HTTP Request POST to 
        create a user and register it with Authy.
        Authy generates a unique ID to the user,
        the variable is stored in 'Auser.id'
    Fields:
        userEmail       =>  Holds user Email sent 
                            in POST request
        userPassword    =>  Holds user Passoword 
                            sent in POST request
        userCPassword   =>  Holds user ConfirmPassword 
                            sent in POST request
        userPhoneNumber =>  Holds user Phone number 
                            sent in POST request
        userName        =>  Holds username sent 
                            in POST request
        data            =>  Holds information 
                            sent in POST request
    CreatedBy:
        Andrew Doser
        9/11/2019
    """
    if request.method != "POST":
        return HttpResponse(status=500)
    data = request.POST

    # Communicate with Michalangelo about how he will communicate 
    # the user data
    userEmail = data['Email']
    userPassword = data['Password']
    userCPassword = data['confirmPassword']
    userPhoneNumber = data['PhoneNumber']
    userName = data['UserName']

    if userPassword == userCPassword:
        # Below is where the user is register with Authy
        # This uses the authy API listed at the top of
        # this file.
        Auser = authy_api.users.create(
        email=userEmail,
        phone=userPhoneNumber, # This needs to be properly formatted i.e. hyphens
        country_code=1)

        # Save the user to SQLite Database
        user = CustomUser(
            email=userEmail,
            password=userPassword, 
            username=userName,
            phoneNumber=userPhoneNumber,
            AuthyIdentity=Auser.id) # Authy generates an ID when a user is registered
        # This ID is used to send the verification code
        user.save()



        # This creates a binding to the Twilio Notifications service. 
        """
        Below the binding is not working due to account error with twilio
        """
        # binding = notifyClient.notify.services(twilioNotifyService) \
        # .bindings.create(
        #     # We recommend using a GUID or other anonymized identifier for Identity
        #     identity=user.twilioIdentity, #This is in the models.py file
        #     binding_type='sms',
        #     address='+1' + user.phoneNumber) # this does not need to be properly formatted

        


        return HttpResponse(user.id)
    else:
        return HttpResponse(status=200)
    
    return HttpResponse(status=500)




@csrf_exempt
def send_tfa_user_view(request):
    """
    Purpose:
        Take data from the HTTP Request POST to
        authenticate the phone number registered
        to user. Must first find user the phone
        number is attached to, then send the User's
        AuthyIdentity to Authy client.
    Fields:
        selectedUser    =>  Holds the CustomUser 
                            that has Phone number 
                            from POST request
        sms             =>  Holds information on 
                            the verification text 
                            sent
    CreatedBy:
        Andrew Doser
        9/11/2019
    """
    if request.method != "POST":
        return HttpResponse(status=500)

    selectedUser = CustomUser.objects.filter(id=F(request.POST['id']))


    # The function below finds the Authy user based on the ID stored in selectedUser
    # it then generates a 7 digit pin and sends it to the phone number registered 
    # with the user in Authy.
    sms = authy_api.users.request_sms(selectedUser.AuthyIdentity)
    if sms.ok():
        return HttpResponse(code=201)
    else:
        return HttpResponse(code=500)

@csrf_exempt
def verify_tfa_user_view(request):
    """
    Purpose:
        Take data from the HTTP Request POST to
        verify the 7 digit pin sent to user. Must 
        first find user the phone number is 
        attached to, then send the User's 
        AuthyIdentity to Authy client.
    Fields:
        selectedUser    =>  Holds the CustomUser 
                            that has Phone number 
                            from POST request
        verification    =>  Holds information on 
                            the verification Authy 
                            did
    CreatedBy:
        Andrew Doser
        9/11/2019
    """
    if request.method != "POST":
        return HttpResponse(status=500)
    selectedUser = CustomUser.objects.filter(id=F(request.POST['id']))


    # The function below finds the Authy user based on the ID stored in selectedUser
    # it then checks the token that was generated by Authy to the one sent in the HTTP
    # POST request.
    verification = authy_api.tokens.verify(selectedUser.AuthyIdentity, token=request.POST['token'])

    if verification.ok:
        return HttpResponse(code=200)
    else:
        return HttpResponse(code=500)


@csrf_exempt
def send_reminder_view(request):
    if request.method != "POST":
        return HttpResponse(status=500)
    selectedUser = CustomUser.objects.filter(id=F(request.POST['id']))
    notification = notifyClient.notify.services(twilioNotifyService) \
    .notifications.create(
        # We recommend using a GUID or other anonymized identifier for Identity
        identity=selectedUser.twilioIdentity,
        body='Knok-Knok! This is your first Notify SMS')


@csrf_exempt
def create_text_view(request):
    """
    Purpose:
        Take data from the HTTP Request POST to
        send a text message to target user.
    Fields:
        data    =>  holds data from HTTP Request Post
        message =>  holds data on the message created
    CreatedBy:
        Andrew Doser
        9/11/2019
    """
    if request.method != "POST":
        return HttpResponse(status=404)
    data = request.POST
    data = request.POST.get('sms') # 'sms' should be the target phone number
    # client.messages.create() both creates and sends the text message
    # it returns a json object with information on it if 'create' passes
    message = smsClient.messages \
                .create(
                    body="Thanks for signing up! You will be reminded!",
                    from_='+15205954045',
                    to=data
                )

    #message.media("https://farm8.staticflickr.com/7090/6941316406_80b4d6d50e_z_d.jpg")




    return HttpResponse(str(message))

class CustomUserAPIView(mixins.CreateModelMixin, generics.ListAPIView):
    permission_classes = []
    authentication_classes = []
    serializer_class = CustomUserSerializer

    def get_queryset(self):
        qs = CustomUser.objects.all()
        query = self.request.GET.get('q')
        if query is not None:
            qs = qs.filter(content__icontains=query)
        return qs

    def post(self, request, *args, **kwargs):
        return self.create(request, *args, **kwargs)


class CustomUserDetailAPIView(mixins.UpdateModelMixin, generics.RetrieveAPIView):
    permission_classes = []
    authentication_classes = []
    queryset = CustomUser.objects.all()
    serializer_class = CustomUserSerializer


    def put(self, request, *args, **kwargs):
        return self.update(request, *args, **kwargs)
