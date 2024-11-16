from rest_framework import permissions

class CustomReadOnly(permissions.BasePermission):

    # 각 개체에 대한 요청
    def has_object_permission(self, request, view, obj):
        if request.method in permissions.SAFE_METHODS: # get 요청
            return True
        return obj.user == request.user # 객체 유저와 요청 유저가 동일하면 True