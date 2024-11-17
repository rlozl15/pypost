from django.urls import path
from rest_framework import routers
from .views import PostViewSet, like_post, CommentViewSet

router = routers.SimpleRouter()
router.register('posts',PostViewSet)
router.register('comments', CommentViewSet)

urlpatterns = router.urls

urlpatterns += [
    path('like/<int:id>/', like_post, name='like_post')
]