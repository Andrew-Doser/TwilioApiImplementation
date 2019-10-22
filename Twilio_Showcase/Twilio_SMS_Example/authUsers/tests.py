from django.test import TestCase
from rest_framework.test import APITestCase
from rest_framework import status
from .models import CustomUser
from rest_framework.reverse import reverse as api_reverse
import json
# Create your tests here.

class CustomUserAPITestCase(APITestCase):
    def setUp(self):
        user = CustomUser.objects.create(
            email='andrew.doser@gridworks-ic.org', 
            username='Andrew Doser', 
            phoneNumber='5035019827',
            password='password123',
            )
        user.save()
        user = CustomUser.objects.create(
            email='divya.kumar@gridworks-ic.org', 
            username='Divya Kumar', 
            phoneNumber='5037544106',
            password='password123',
            )
        user.save()

        user = CustomUser.objects.create(
            email='test1@example.com', 
            username='Test 1', 
            phoneNumber='0000000000',
            password='password123',
            )
        user.save()
        user = CustomUser.objects.create(
            email='test2@example.com', 
            username='Test 2', 
            phoneNumber='1111111111',
            password='password123',
            )
        user.save()


    def test_created_user(self):
        qs = CustomUser.objects.filter(username='Andrew Doser')
        self.assertEqual(qs.count(), 1)

    def test_post_user_api(self):
        url = api_reverse('api:viewlist')
        data = {
            'email'         :'test4@example.com', 
            'username'      :'Test 4', 
            'phoneNumber'   :'3333333333',
            'password'      :'password123',
        }
        response = self.client.post(url, data=data, format='json')
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)

    def test_post_user_api_FAIL(self):
        url = api_reverse('api:viewlist')
        data = {
            'email'         :'divya.kumar@gridworks-ic.org', 
            'username'      :'Divya Kumar', 
            'password'      :'password123',
        }
        response = self.client.post(url, data=data, format='json')
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
    def test_put_user_api(self):
        url = api_reverse('api:viewlist')
        data = {
            'id'            :'1',
            'email'         :'drew.doser@gmail.com', 
            'username'      :'Drew Doser', 
            'phoneNumber'   :'5035019827',
            'password'      :'password123',
        }
        response = self.client.put(url, data=data, format='json')
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        selectedUser = CustomUser.objects.filter(phoneNumber='5035019827').first()
        self.assertEqual(getattr(selectedUser, 'email'), 'drew.doser@gmail.com')
    def test_put_CREATE_user_api(self):
        url = api_reverse('api:viewlist')
        data = {
            'email'         :'drew.doser@gmail.com', 
            'username'      :'Drew Doser', 
            'phoneNumber'   :'5032465542',
            'password'      :'password123',
        }
        response = self.client.put(url, data=data, format='json')
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        selectedUser = CustomUser.objects.filter(phoneNumber='5032465542').first()
        self.assertEqual(getattr(selectedUser, 'email'), 'drew.doser@gmail.com')
    
    def test_patch_user_api(self):
        url = api_reverse('api:viewlist')
        data = {
            'id'            :'1',
            'email'         :'drew.doser@gmail.com', 
            'username'      :'Drew Doser', 
            'phoneNumber'   :'5035019827',
            'password'      :'password123',
        }
        response = self.client.patch(url, data=data, format='json')
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        selectedUser = CustomUser.objects.filter(phoneNumber='5035019827').first()
        self.assertEqual(getattr(selectedUser, 'email'), 'drew.doser@gmail.com')
    
    def test_patch_user_api_FAIL(self):
        url = api_reverse('api:viewlist')
        data = {
            'id'            :'1',
            'username'      :'Drew Doser', 
            'phoneNumber'   :'5035019827',
            'password'      :'password123',
        }
        response = self.client.patch(url, data=data, format='json')
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
        

    def test_get_object_user_api(self):
        url = api_reverse('api:viewlist')
        response = self.client.get(url, data={'id':1}, format='json')
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.data['email'], 'andrew.doser@gridworks-ic.org')
    

    def test_get_object_user_api_FAIL(self):
        url = api_reverse('api:viewlist')
        response = self.client.get(url, data={'id':5}, format='json')
        self.assertEqual(response.status_code, status.HTTP_404_NOT_FOUND)
        self.assertEqual(response.data['detail'], 'Not found.')
 
    def test_get_all_users_api(self):
        url = api_reverse('api:viewlist')
        response = self.client.get(url, format='json')
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        json_data = json.dumps(response.data)
        item_dict = json.loads(json_data)
        qs = CustomUser.objects.all()
        self.assertEqual(len(item_dict[0]), qs.count())


    def test_delete_object_user_api(self):
        url = api_reverse('api:viewlist')
        user = CustomUser.objects.create(
            email='test4@example.com', 
            username='Test 4', 
            phoneNumber='3333333333',
            password='password123',
            )
        user.save()
        selectedUser = CustomUser.objects.filter(id='5').first()
        self.assertEqual(getattr(selectedUser, 'email'), 'test4@example.com')
        response = self.client.delete(url, data={'id':5}, format='json')
        self.assertEqual(response.status_code, status.HTTP_204_NO_CONTENT)
        selectedUser = CustomUser.objects.filter(id='5').first()
        self.assertEqual(selectedUser, None)

    def test_delete_object_user_api_FAIL(self):
        url = api_reverse('api:viewlist')
        selectedUser = CustomUser.objects.filter(id='5').first()
        self.assertEqual(selectedUser, None)
        response = self.client.delete(url, data={'id':5}, format='json')
        self.assertEqual(response.status_code, status.HTTP_404_NOT_FOUND)
    def test_Send_SMS_api(self):
        url = api_reverse('api:sms')
        response = self.client.get(url, data={'id':1}, format='json')
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        data = response.content.decode('utf8').replace("'", '"')
        check = False
        if 'pending' in data:
            check = True
        self.assertEqual(check, True)

        

        
    
        


    


        
