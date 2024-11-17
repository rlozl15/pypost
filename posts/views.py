from django_filters.rest_framework import DjangoFilterBackend
from rest_framework import viewsets, status
from rest_framework.decorators import api_view, permission_classes
from rest_framework.generics import get_object_or_404
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response

from users.models import Profile
from .models import Post, Comment
from .permissions import CustomReadOnly
from .serializers import PostSerializer, PostCreateSerializer, CommentSerializer, CommentCreateSerializer


class PostViewSet(viewsets.ModelViewSet):
    queryset = Post.objects.all().order_by('-id') # 내림차순
    permission_classes = [CustomReadOnly]
    filter_backends = [DjangoFilterBackend]
    filterset_fields = ['author','likes']

    def get_serializer_class(self):
        if self.action in ["list", "retrieve"]:
            return PostSerializer
        return PostCreateSerializer

    def perform_create(self, serializer):
        profile = Profile.objects.get(user = self.request.user)
        serializer.save(author = self.request.user, profile = profile)

@api_view(["POST"])
@permission_classes([IsAuthenticated])
def like_post(request, id):
    post = get_object_or_404(Post, id=id)
    if request.user in post.likes.all():
        post.likes.remove(request.user)
    else:
        post.likes.add(request.user)
    return Response(status=status.HTTP_200_OK)

class CommentViewSet(viewsets.ModelViewSet):
    queryset = Comment.objects.all().order_by('id') # 오름차순
    permission_classes = [CustomReadOnly]

    def get_serializer_class(self):
        if self.action in ["list","retrieve"]:
            return CommentSerializer
        return CommentCreateSerializer

    def perform_create(self, serializer):
        profile = Profile.objects.get(user=self.request.user)
        serializer.save(author=self.request.user, profile=profile)