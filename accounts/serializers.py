import logging
from rest_framework import serializers
from django.contrib.auth import get_user_model
from django.contrib.auth.password_validation import validate_password
from django.core.exceptions import ValidationError as DjangoValidationError
from rest_framework_simplejwt.serializers import TokenObtainPairSerializer

User = get_user_model()
logger = logging.getLogger(__name__)


class PublicUserSerializer(serializers.ModelSerializer):
    """
    Public representation of a user (e.g. landlord on public property listings).
    Excludes sensitive personal information such as email, phone, last_login, etc.
    """
    class Meta:
        model = User
        fields = ['id', 'username', 'first_name', 'last_name', 'role']
        read_only_fields = ['id', 'username', 'first_name', 'last_name', 'role']


class UserSerializer(serializers.ModelSerializer):
    """
    Private authenticated user representation for /api/auth/me/.
    """
    class Meta:
        model = User
        fields = [
            'id', 
            'username', 
            'first_name', 
            'last_name', 
            'email', 
            'role', 
            'phone', 
            'email_verified', 
            'created_at'
        ]
        read_only_fields = ['id', 'username', 'email', 'role', 'created_at', 'email_verified']


class SignupSerializer(serializers.ModelSerializer):
    username = serializers.CharField(required=False, allow_blank=True)
    password = serializers.CharField(write_only=True, required=True, style={'input_type': 'password'})
    name = serializers.CharField(write_only=True, required=False, allow_blank=True)
    first_name = serializers.CharField(required=False, allow_blank=True, default='')
    last_name = serializers.CharField(required=False, allow_blank=True, default='')
    phone = serializers.CharField(required=False, allow_blank=True, default='')
    
    class Meta:
        model = User
        fields = ['username', 'email', 'password', 'role', 'phone', 'first_name', 'last_name', 'name']
    
    def to_internal_value(self, data):
        # Support legacy 'name' field from frontend forms when 'username' is omitted
        mutable_data = data.copy() if hasattr(data, 'copy') else dict(data)
        if not mutable_data.get('username') and mutable_data.get('name'):
            mutable_data['username'] = mutable_data['name'].strip()
        return super().to_internal_value(mutable_data)

    def validate_email(self, value):
        if not value:
            raise serializers.ValidationError("Email is required.")
        normalized_email = value.strip().lower()
        if User.objects.filter(email__iexact=normalized_email).exists():
            raise serializers.ValidationError("A user with this email already exists.")
        return normalized_email

    def validate_username(self, value):
        if not value or not value.strip():
            raise serializers.ValidationError("Username is required.")
        cleaned_username = value.strip()
        if User.objects.filter(username__iexact=cleaned_username).exists():
            raise serializers.ValidationError("A user with that username already exists.")
        return cleaned_username

    def validate_role(self, value):
        valid_roles = ['tenant', 'landlord']
        if not value or value.lower() not in valid_roles:
            raise serializers.ValidationError("Role must be either 'tenant' or 'landlord'.")
        return value.lower()

    def validate_password(self, value):
        if not value:
            raise serializers.ValidationError("Password cannot be empty.")
        try:
            validate_password(value)
        except DjangoValidationError as e:
            raise serializers.ValidationError(list(e.messages))
        return value

    def validate(self, attrs):
        if not attrs.get('username'):
            raise serializers.ValidationError({"username": "This field is required."})
        if not attrs.get('email'):
            raise serializers.ValidationError({"email": "This field is required."})

        # Populate first_name / last_name from name if not provided
        name = attrs.pop('name', None)
        if name:
            name_parts = name.strip().split(' ', 1)
            if not attrs.get('first_name'):
                attrs['first_name'] = name_parts[0]
            if len(name_parts) > 1 and not attrs.get('last_name'):
                attrs['last_name'] = name_parts[1]

        return attrs

    def create(self, validated_data):
        password = validated_data.pop('password')
        
        # Enforce server-controlled security fields (never allow public escalation)
        validated_data['is_staff'] = False
        validated_data['is_superuser'] = False
        validated_data['is_active'] = True
        validated_data['email_verified'] = False

        user = User.objects.create_user(password=password, **validated_data)
        logger.info(f"User created successfully: {user.username} (role: {user.role})")
        return user


class LoginSerializer(TokenObtainPairSerializer):
    def validate(self, attrs):
        raw_username = attrs.get('username', '').strip()
        # Support logging in via email as well as username
        if '@' in raw_username:
            try:
                matched_user = User.objects.get(email__iexact=raw_username)
                attrs['username'] = matched_user.username
            except (User.DoesNotExist, User.MultipleObjectsReturned):
                pass

        data = super().validate(attrs)
        # Provide both 'access' (standard JWT) and 'token' (frontend expectation)
        access_token = data['access']
        data['token'] = access_token
        data['user'] = UserSerializer(self.user).data
        return data


class LogoutSerializer(serializers.Serializer):
    refresh = serializers.CharField(required=False, allow_blank=True)
