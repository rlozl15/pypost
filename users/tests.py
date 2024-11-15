from django.test import TestCase
from rest_framework import status
from rest_framework.test import APIClient
from django.contrib.auth.models import User


class RegisterTest(TestCase):
    def setUp(self):
        self.client = APIClient()
        self.user = User.objects.create_user(
            username="test_user",
            email="test@test.com",
            password="testpw!!",
        )

    def test_create_user(self):
        user_data = {
            "username":"test_user2",
            "email":"test2@test.com",
            "password":"testpw!!!",
            "password2":"testpw!!!",
        }
        response = self.client.post("/user/register/",user_data,format="json")
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        self.assertEqual(response.data["username"], user_data["username"])

    def test_invalid_username(self):
        invalid_user_data = {
            "username":"test_user",
            "email":"test2@test.com",
            "password":"testpw!!!",
            "password2":"testpw!!!",
        }
        response = self.client.post("/user/register/",invalid_user_data,format="json")
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)

    def test_invalid_password(self):
        invalid_user_data = {
            "username":"test_user2",
            "email":"test2@test.com",
            "password":"testpw!!!",
            "password2":"testpw",
        }
        response = self.client.post("/user/register/",invalid_user_data,format="json")
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)

    def test_invalid_email(self):
        invalid_user_data = {
            "username": "test_user2",
            "email": "test@test.com",
            "password": "testpw!!!",
            "password2": "testpw!!!",
        }
        response = self.client.post("/user/register/", invalid_user_data, format="json")
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)