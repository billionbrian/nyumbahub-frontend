import logging
import traceback
from rest_framework import status
from rest_framework.decorators import api_view, permission_classes
from rest_framework.permissions import AllowAny, IsAuthenticated
from rest_framework.response import Response
from rest_framework_simplejwt.views import TokenObtainPairView
from .serializers import SignupSerializer, LoginSerializer, UserSerializer

logger = logging.getLogger(__name__)


@api_view(['POST'])
@permission_classes([AllowAny])
def signup(request):
    logger.info(f"Signup request received with data: {request.data}")
    try:
        serializer = SignupSerializer(data=request.data)
        if serializer.is_valid():
            logger.info("Serializer validation passed, creating user")
            user = serializer.save()
            logger.info(f"User created successfully: {user.username}")
            return Response(
                {'message': 'Account created successfully'},
                status=status.HTTP_201_CREATED
            )
        logger.error(f"Serializer validation failed: {serializer.errors}")
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)
    except Exception as e:
        logger.error(f"Signup error: {str(e)}")
        logger.error(f"Traceback: {traceback.format_exc()}")
        return Response(
            {'error': str(e), 'detail': 'Internal server error occurred'},
            status=status.HTTP_500_INTERNAL_SERVER_ERROR
        )


@api_view(['GET'])
@permission_classes([IsAuthenticated])
def current_user(request):
    """Get current authenticated user data"""
    try:
        serializer = UserSerializer(request.user)
        return Response(serializer.data)
    except Exception as e:
        logger.error(f"Error fetching current user: {str(e)}")
        return Response(
            {'error': str(e)},
            status=status.HTTP_500_INTERNAL_SERVER_ERROR
        )


class LoginView(TokenObtainPairView):
    serializer_class = LoginSerializer
