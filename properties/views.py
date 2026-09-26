from rest_framework import viewsets, permissions, status, filters
from rest_framework.decorators import api_view, permission_classes, action
from rest_framework.parsers import MultiPartParser, FormParser, JSONParser
from rest_framework.response import Response
from rest_framework.pagination import PageNumberPagination
from django_filters.rest_framework import DjangoFilterBackend
from .models import Property, PropertyImage
from .serializers import PropertySerializer, PropertyImageSerializer
from .permissions import IsLandlord, IsPropertyOwner
import logging

logger = logging.getLogger(__name__)


class PropertyPagination(PageNumberPagination):
    page_size = 12
    page_size_query_param = 'page_size'
    max_page_size = 100


class PropertyViewSet(viewsets.ModelViewSet):
    queryset = Property.objects.all()
    serializer_class = PropertySerializer
    pagination_class = PropertyPagination
    filter_backends = [DjangoFilterBackend, filters.SearchFilter, filters.OrderingFilter]
    filterset_fields = ['property_type', 'bedrooms', 'bathrooms', 'status', 'available', 'landlord']
    search_fields = ['title', 'description', 'location']
    ordering_fields = ['rent_amount', 'created_at', 'bedrooms']
    ordering = ['-created_at']

    @action(detail=False, methods=['get'], permission_classes=[permissions.IsAuthenticated])
    def mine(self, request):
        """Returns listings belonging to the currently authenticated landlord"""
        queryset = self.get_queryset().filter(landlord=request.user)
        page = self.paginate_queryset(queryset)
        if page is not None:
            serializer = self.get_serializer(page, many=True)
            return self.get_paginated_response(serializer.data)
        serializer = self.get_serializer(queryset, many=True)
        return Response(serializer.data)
    
    def get_queryset(self):
        queryset = Property.objects.all()

        # Partial location search if explicitly passed
        location = self.request.query_params.get('location')
        if location:
            queryset = queryset.filter(location__icontains=location.strip())
        
        # Safe numeric filtering for price range
        min_price = self.request.query_params.get('min_price')
        max_price = self.request.query_params.get('max_price')
        
        if min_price is not None:
            try:
                min_val = float(min_price)
                queryset = queryset.filter(rent_amount__gte=min_val)
            except (ValueError, TypeError):
                pass
        if max_price is not None:
            try:
                max_val = float(max_price)
                queryset = queryset.filter(rent_amount__lte=max_val)
            except (ValueError, TypeError):
                pass
        
        return queryset
    
    def get_permissions(self):
        if self.action in ['list', 'retrieve']:
            permission_classes = [permissions.AllowAny]
        elif self.action == 'create':
            permission_classes = [permissions.IsAuthenticated, IsLandlord]
        else:
            permission_classes = [permissions.IsAuthenticated, IsLandlord, IsPropertyOwner]
        return [permission() for permission in permission_classes]
    
    def perform_create(self, serializer):
        # Force landlord to always be the authenticated user (client cannot override)
        property_obj = serializer.save(landlord=self.request.user)
        # Check if multiple images were submitted during creation
        files = self.request.FILES.getlist('images')
        for idx, file in enumerate(files):
            PropertyImage.objects.create(
                property=property_obj,
                image=file,
                is_primary=(idx == 0)
            )

    def perform_update(self, serializer):
        # Ensure landlord cannot be transferred during update
        property_obj = serializer.save()
        files = self.request.FILES.getlist('images')
        for idx, file in enumerate(files):
            PropertyImage.objects.create(
                property=property_obj,
                image=file,
                is_primary=not property_obj.images.exists() and idx == 0
            )

    @action(detail=True, methods=['post'], parser_classes=[MultiPartParser, FormParser, JSONParser], permission_classes=[permissions.IsAuthenticated, IsLandlord, IsPropertyOwner])
    def upload_images(self, request, pk=None):
        """Allows landlord to upload multiple image files or image URLs to a property"""
        property_obj = self.get_object()
        created_images = []

        files = request.FILES.getlist('images') or request.FILES.getlist('image')
        for idx, file in enumerate(files):
            is_primary = not property_obj.images.exists() and idx == 0
            img = PropertyImage.objects.create(
                property=property_obj,
                image=file,
                is_primary=is_primary
            )
            created_images.append(img)

        urls = request.data.get('image_urls') or []
        if isinstance(urls, str):
            import json
            try:
                urls = json.loads(urls)
            except Exception:
                urls = [urls]
        for idx, url in enumerate(urls):
            is_primary = not property_obj.images.exists() and not created_images and idx == 0
            img = PropertyImage.objects.create(
                property=property_obj,
                image_url=url,
                is_primary=is_primary
            )
            created_images.append(img)

        # Sync primary image to property field if empty
        if not property_obj.image and files:
            property_obj.image = files[0]
            property_obj.save(update_fields=['image'])
        elif not property_obj.image_url and urls:
            property_obj.image_url = urls[0]
            property_obj.save(update_fields=['image_url'])

        return Response(
            PropertySerializer(property_obj, context={'request': request}).data,
            status=status.HTTP_201_CREATED
        )

    @action(detail=True, methods=['delete'], url_path='images/(?P<image_id>[^/.]+)', permission_classes=[permissions.IsAuthenticated, IsLandlord, IsPropertyOwner])
    def delete_image(self, request, pk=None, image_id=None):
        property_obj = self.get_object()
        try:
            img = property_obj.images.get(id=image_id)
            img.delete()
            return Response({'message': 'Image removed successfully'}, status=status.HTTP_200_OK)
        except PropertyImage.DoesNotExist:
            return Response({'error': 'Image not found'}, status=status.HTTP_404_NOT_FOUND)



@api_view(['POST'])
@permission_classes([permissions.AllowAny])
def initiate_payment(request):
    """
    Initiate M-Pesa payment for property booking
    """
    try:
        phone = request.data.get('phone')
        amount = request.data.get('amount')
        
        if not phone or not amount:
            return Response(
                {'error': 'Phone number and amount are required'},
                status=status.HTTP_400_BAD_REQUEST
            )
        
        logger.info(f"Payment initiation request: phone={phone}, amount={amount}")
        
        # TODO: Integrate with actual M-Pesa API
        # For now, return a mock response
        return Response({
            'message': 'STK Push sent successfully',
            'phone': phone,
            'amount': amount,
            'status': 'pending'
        }, status=status.HTTP_200_OK)
        
    except Exception as e:
        logger.error(f"Payment initiation error: {str(e)}")
        return Response(
            {'error': 'Payment initiation failed'},
            status=status.HTTP_500_INTERNAL_SERVER_ERROR
        )

