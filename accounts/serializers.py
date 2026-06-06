import logging
from rest_framework import serializers
from django.contrib.auth import get_user_model
from rest_framework_simplejwt.serializers import TokenObtainPairSerializer

User = get_user_model()
logger = logging.getLogger(__name__)


class UserSerializer(serializers.ModelSerializer):
    class Meta:
        model = User
        fields = ['id', 'username', 'email', 'role', 'phone', 'created_at']
        read_only_fields = ['id', 'created_at']


class SignupSerializer(serializers.ModelSerializer):
    password = serializers.CharField(write_only=True, required=True, style={'input_type': 'password'})
    name = serializers.CharField(write_only=True, required=False)
    
    class Meta:
        model = User
        fields = ['username', 'email', 'password', 'role', 'phone', 'name']
    
    def validate_role(self, value):
        logger.info(f"Validating role: {value}")
        valid_roles = ['tenant', 'landlord']
        if value not in valid_roles:
            raise serializers.ValidationError("Role must be either 'tenant' or 'landlord'.")
        return value
    
    def validate(self, attrs):
        logger.info(f"Validating signup data: {attrs}")
        # If username is not provided but name is, use name as username
        if 'username' not in attrs and 'name' in attrs:
            attrs['username'] = attrs.pop('name')
            logger.info(f"Converted name to username: {attrs['username']}")
        # Remove name field if present (we don't store it separately)
        if 'name' in attrs:
            attrs.pop('name')
        if 'username' not in attrs:
            logger.error("Username field is missing")
            raise serializers.ValidationError({"username": "This field is required."})
        return attrs
    
    def create(self, validated_data):
        logger.info(f"Creating user with validated data: {validated_data}")
        password = validated_data.pop('password')
        user = User.objects.create_user(**validated_data)
        user.set_password(password)
        user.save()
        logger.info(f"User created successfully: {user.username}")
        return user


class LoginSerializer(TokenObtainPairSerializer):
    def validate(self, attrs):
        data = super().validate(attrs)
        data['token'] = data.pop('access')
        data['user'] = UserSerializer(self.user).data
        return data
