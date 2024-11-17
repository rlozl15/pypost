from django.test import TestCase
from rest_framework import status
from rest_framework.test import APIClient
from django.core.files.uploadedfile import SimpleUploadedFile

from django.contrib.auth.models import User
from rest_framework.authtoken.models import Token
from posts.models import Post, Comment


# image = SimpleUploadedFile(name='test_image.jpg', content=open("media/default.png", 'rb').read(), content_type='image/jpeg')

class PostTest(TestCase):
    def setUp(self):
        self.client = APIClient()
        user_data = {
            "username": "test_user",
            "email": "test@test.com",
            "password": "testpw!!",
        }
        self.user = User.objects.create_user(**user_data)
        self.token = Token.objects.create(user=self.user)
        post_data = {
            "author": self.user,
            "profile": self.user.profile,
            "title": "test_title",
            "body": "this is body",
            "category": "backend",
        }
        self.post = Post.objects.create(**post_data)

    def test_get_post_list(self):
        response = self.client.get('/posts/')
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertIsInstance(response.data["results"], list)
        self.assertGreater(response.data["count"], 0)

    def test_get_single_post(self):
        response = self.client.get(f"/posts/{self.post.id}/")
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.data['title'], self.post.title)

    def test_get_invalid_single_post(self):
        response = self.client.get("/posts/99999/")
        self.assertEqual(response.status_code, status.HTTP_404_NOT_FOUND)

    def test_create_post(self):
        with open('media/default.png', 'rb') as f:
            image = SimpleUploadedFile('test_image.jpg', f.read(), content_type='image/jpeg')
        new_post = {
            "title": "test_title",
            "body": "this is body",
            "category": "backend",
            "image": image,
        }
        self.client.credentials(HTTP_AUTHORIZATION=f'Token {self.token.key}')
        response = self.client.post("/posts/", data=new_post, format="multipart")
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        self.assertEqual(response.data['title'], new_post['title'])

    def test_create_post_without_authorization(self):
        new_post = {
            "title":"test_title",
            "body":"this is body",
            "category":"backend",
        }
        self.client.credentials()
        response = self.client.post("/posts/",new_post,format="json")
        self.assertEqual(response.status_code, status.HTTP_401_UNAUTHORIZED)

    def test_update_post(self):
        new_data = {
            "title":"new_title",
            "body":"this is body",
            "category":"backend",
        }
        self.client.credentials(HTTP_AUTHORIZATION=f'Token {self.token.key}')
        response = self.client.put(f"/posts/{self.post.id}/", data=new_data, format="json")
        self.assertEqual(response.status_code, status.HTTP_200_OK)

class LikeTest(TestCase):
    def setUp(self):
        self.client = APIClient()
        self.user = User.objects.create_user(
            username = "test_user1",
            email = "test@test.com",
            password = "testpassword!"
        )
        self.token = Token.objects.create(user=self.user)
        self.post = Post.objects.create(
            author = self.user,
            profile = self.user.profile,
            title = "test_title",
            body = "this is body",
            category = "backend",
        )

    def test_like_action(self):
        user2 = User.objects.create_user(
            username = "test_user2",
            email = "test2@test.com",
            password = "test2password!"
        )
        token = Token.objects.create(user=user2)
        self.client.credentials(HTTP_AUTHORIZATION=f'Token {token.key}')

        response = self.client.post(f"/like/{self.post.id}/")
        self.assertEqual(response.status_code, status.HTTP_200_OK)

        self.post.refresh_from_db()
        self.assertIn(user2, self.post.likes.all())
        self.assertIn(self.post, user2.like_posts.all())

    def test_unlike(self):
        user2 = User.objects.create_user(
            username = "test_user2",
            email = "test2@test.com",
            password = "test2password!"
        )
        token = Token.objects.create(user=user2)
        self.client.credentials(HTTP_AUTHORIZATION=f'Token {token.key}')
        # like check
        self.post.likes.add(user2)

        response = self.client.post(f"/like/{self.post.id}/")
        self.assertEqual(response.status_code, status.HTTP_200_OK)

        self.post.refresh_from_db()
        self.assertNotIn(user2, self.post.likes.all())
        self.assertNotIn(self.post, user2.like_posts.all())

    def test_like_without_authorization(self):
        response = self.client.post(f"/like/{self.post.id}/")
        self.assertEqual(response.status_code, status.HTTP_401_UNAUTHORIZED)


class CommentsTest(TestCase):
    def setUp(self):
        self.client = APIClient()
        self.user = User.objects.create_user(
            username = "test_user1",
            email = "test@test.com",
            password = "testpassword!"
        )
        self.token = Token.objects.create(user=self.user)
        self.post = Post.objects.create(
            author = self.user,
            profile = self.user.profile,
            title = "test_title",
            body = "this is body",
            category = "backend",
        )
        self.comment = Comment.objects.create(
            author = self.user,
            profile = self.user.profile,
            post = self.post,
            text = "test_comment",
        )

    def test_get_comments_list(self):
        response = self.client.get("/comments/")
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertIsInstance(response.data['results'],list)
        self.assertGreater(response.data['count'],0)

    def test_create_comment(self):
        self.client.credentials(HTTP_AUTHORIZATION=f'Token {self.token.key}')
        response = self.client.post(
            "/comments/",
            {"post":self.post.id, "text":"new_comment"},
            format="json"
        )
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)

    def test_get_single_comment(self):
        response = self.client.get(f"/comments/{self.comment.id}/")
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.data["text"],self.comment.text)

    def test_get_invalid_single_comment(self):
        response = self.client.get("/comments/999/")
        self.assertEqual(response.status_code, status.HTTP_404_NOT_FOUND)

    def test_update_comment(self):
        self.client.credentials(HTTP_AUTHORIZATION=f'Token {self.token.key}')
        response = self.client.put(f"/comments/{self.comment.id}/",
                                   {"post":self.post.id,
                                         "text":"updated_comment"},
                                   fromat = "json")
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.data["text"],"updated_comment")
