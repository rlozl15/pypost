from rest_framework import permissions

class CustomReadOnly(permissions.BasePermission):
    # 글 조회는 누구나, 생성은 인증된 유저
    def has_permission(self, request, view):
        if request.method == "GET":
            return True
        return request.user.is_authenticated

    # 특정 글 조회는 누구나, 수정/삭제는 글 작성자
    def has_object_permission(self, request, view, obj):
        if request.method in permissions.SAFE_METHODS:
            return True
        return obj.author == request.user