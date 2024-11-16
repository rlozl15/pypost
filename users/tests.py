from django.test import TestCase
from rest_framework import status
from rest_framework.test import APIClient
from django.contrib.auth.models import User
from rest_framework.authtoken.models import Token


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
        response = self.client.post("/user/register/", user_data, format="json")
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        self.assertEqual(response.data["username"], user_data["username"])

    def test_invalid_username(self):
        invalid_user_data = {
            "username":"test_user",
            "email":"test2@test.com",
            "password":"testpw!!!",
            "password2":"testpw!!!",
        }
        response = self.client.post("/user/register/", invalid_user_data, format="json")
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)

    def test_invalid_password(self):
        invalid_user_data = {
            "username":"test_user2",
            "email":"test2@test.com",
            "password":"testpw!!!",
            "password2":"testpw",
        }
        response = self.client.post("/user/register/", invalid_user_data, format="json")
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


class UserBaseTest(TestCase):
    def setUp(self):
        self.client = APIClient()
        user_data = {
            "username":"test_user",
            "email":"test@test.com",
            "password":"testpw!!",
        }
        self.user = User.objects.create_user(**user_data)
        self.token = Token.objects.create(user=self.user)


class LoginTest(UserBaseTest):
    def test_login(self):
        login_data = {
            "username":"test_user",
            "password":"testpw!!",
        }
        response = self.client.post("/user/login/", login_data, format="json")
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertIn("token", response.data)

    def test_invalid_login_with_nonexistent_user(self):
        login_data = {
            "username":"nonexistentuser",
            "password":"testpw!!",
        }
        response = self.client.post("/user/login/", login_data, format="json")
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)

    def test_invalid_login_with_wrong_password(self):
        login_data = {
            "username":"test_user",
            "password":"wrongpassword",
        }
        response = self.client.post("/user/login/", login_data, format="json")
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)


class ProfileTest(UserBaseTest):
    def test_profile(self):
        nickname = self.user.profile.nickname
        response = self.client.get(f"/user/profile/{self.user.id}/")
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.data["nickname"], nickname)


    def test_profile_update_with_authentication(self):
        update_data = {
            "nickname":"testname",
            "position":"backend",
            "subjects":"Django, RestfulAPI"
        }
        self.client.credentials(HTTP_AUTHORIZATION='Token ' + self.token.key)
        response = self.client.put(f"/user/profile/{self.user.id}/", update_data, format="json")
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.data["nickname"], update_data["nickname"])

    def test_profile_update_without_authentication(self):
        update_data = {
            "nickname":"testname",
            "position":"backend",
            "subjects":"Django, RestfulAPI"
        }
        response = self.client.put(f"/user/profile/{self.user.id}/", update_data, format="json")
        self.assertEqual(response.status_code, status.HTTP_401_UNAUTHORIZED)

    def test_profile_update_with_invalid_authentication(self):
        update_data = {
            "nickname": "testname",
            "position": "backend",
            "subjects": "Django, RestfulAPI"
        }
        self.client.credentials(HTTP_AUTHORIZATION='Token ' + "invalid_token")
        response = self.client.put(f"/user/profile/{self.user.id}/", update_data, format="json")
        self.assertEqual(response.status_code, status.HTTP_401_UNAUTHORIZED)

