from django.contrib.auth.models import User  # 기본 제공 사용자 모델
from django.contrib.auth.password_validation import validate_password # 기본 pw 검증 도구
from django.contrib.auth import authenticate
from rest_framework import serializers
from rest_framework.authtoken.models import Token     # 토큰 모델
from rest_framework.validators import UniqueValidator # 중복 방지 도구

class RegisterSerializer(serializers.ModelSerializer):
    email = serializers.EmailField(
        required=True,
        validators=[UniqueValidator(queryset=User.objects.all())], # 이메일 중복 검증
    )
    password = serializers.CharField(
        write_only=True,
        required=True,
        validators=[validate_password], # 비밀번호 검증
    )
    # 비밀번호 확인을 위한 필드
    password2 = serializers.CharField(
        write_only=True,
        required=True,
    )

    class Meta:
        model = User
        fields = ["username","password","password2","email"]

    def validate(self, data):
        if data['password'] != data['password2']:
            raise serializers.ValidationError(
                {'password': '비밀번호가 일치하지 않습니다.'}
            )
        return data

    def create(self, validated_data): # create 요청에 대해 create 메소드 오버라이딩 (유저 생성 및 토큰 생성)
        user = User.objects.create_user(
            username=validated_data['username'],
            email=validated_data['email'],
        )
        user.set_password(validated_data['password'])
        user.save()
        token = Token.objects.create(user=user)
        return user

class LoginSerializer(serializers.Serializer):
    username = serializers.CharField(required=True)
    password = serializers.CharField(required=True, write_only=True)

    def validate(self, data):
        user = authenticate(**data)
        if user:
            token = Token.objects.get(user=user)
            return token
        raise serializers.ValidationError(
            {"error":"Unable to log in with provided credentials."}
        )