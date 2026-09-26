from decimal import Decimal
from unittest.mock import patch
from django.test import TestCase
from django.urls import reverse
from rest_framework.test import APIClient
from rest_framework import status
from django.contrib.auth import get_user_model
from rest_framework_simplejwt.tokens import RefreshToken
from .models import Property
from .serializers import PropertySerializer

User = get_user_model()


class PropertyModelAndCoordinateTests(TestCase):
    def setUp(self):
        self.landlord = User.objects.create_user(
            username='landlord_tester',
            email='landlord_tester@example.com',
            password='Password123!',
            role='landlord'
        )

    def test_valid_coordinates_saved_correctly(self):
        prop = Property.objects.create(
            landlord=self.landlord,
            title='Valid Coords House',
            description='Test description',
            location='Kilifi',
            latitude=Decimal('-3.626812'),
            longitude=Decimal('39.850127'),
            rent_amount=7000.00
        )
        self.assertEqual(prop.latitude, Decimal('-3.626812'))
        self.assertEqual(prop.longitude, Decimal('39.850127'))
        self.assertIsNotNone(prop.updated_at)

    def test_updated_at_changes_on_modification(self):
        prop = Property.objects.create(
            landlord=self.landlord,
            title='Timestamp Test',
            description='Test description',
            location='Kilifi',
            latitude=Decimal('-3.626812'),
            longitude=Decimal('39.850127'),
            rent_amount=7000.00
        )
        initial_updated_at = prop.updated_at
        prop.rent_amount = 7500.00
        prop.save()
        prop.refresh_from_db()
        self.assertGreaterEqual(prop.updated_at, initial_updated_at)

    def test_serializer_rejects_invalid_latitude(self):
        data = {
            'title': 'Bad Lat',
            'description': 'Test',
            'rent_amount': 5000.00,
            'bedrooms': 1,
            'bathrooms': 1,
            'property_type': 'single',
            'latitude': 95.000000,
            'longitude': 39.850000
        }
        serializer = PropertySerializer(data=data)
        self.assertFalse(serializer.is_valid())
        self.assertIn('latitude', serializer.errors)

    def test_serializer_rejects_invalid_longitude(self):
        data = {
            'title': 'Bad Lon',
            'description': 'Test',
            'rent_amount': 5000.00,
            'bedrooms': 1,
            'bathrooms': 1,
            'property_type': 'single',
            'latitude': -3.620000,
            'longitude': 195.000000
        }
        serializer = PropertySerializer(data=data)
        self.assertFalse(serializer.is_valid())
        self.assertIn('longitude', serializer.errors)

    def test_serializer_requires_coordinates_on_create(self):
        data = {
            'title': 'Missing Coords',
            'description': 'Test',
            'rent_amount': 5000.00,
            'bedrooms': 1,
            'bathrooms': 1,
            'property_type': 'single'
        }
        serializer = PropertySerializer(data=data)
        self.assertFalse(serializer.is_valid())
        self.assertIn('coordinates', serializer.errors)

    def test_legacy_property_with_null_coordinates_serializes_cleanly(self):
        legacy_prop = Property.objects.create(
            landlord=self.landlord,
            title='Legacy House Without Coords',
            description='Existing legacy listing',
            location='Kilifi Town Center',
            latitude=None,
            longitude=None,
            rent_amount=4500.00
        )
        serializer = PropertySerializer(legacy_prop)
        self.assertIsNone(serializer.data['latitude'])
        self.assertIsNone(serializer.data['longitude'])
        self.assertEqual(serializer.data['location'], 'Kilifi Town Center')


class PropertyCreationAndUpdateTests(TestCase):
    def setUp(self):
        self.client = APIClient()
        self.properties_url = reverse('property-list')

        # Landlord 1
        self.landlord1 = User.objects.create_user(
            username='landlord1',
            email='landlord1@example.com',
            password='Password123!',
            role='landlord',
            phone='+254711000001'
        )
        self.token_landlord1 = str(RefreshToken.for_user(self.landlord1).access_token)

        # Landlord 2
        self.landlord2 = User.objects.create_user(
            username='landlord2',
            email='landlord2@example.com',
            password='Password123!',
            role='landlord',
            phone='+254711000002'
        )
        self.token_landlord2 = str(RefreshToken.for_user(self.landlord2).access_token)

        # Tenant
        self.tenant = User.objects.create_user(
            username='tenant1',
            email='tenant1@example.com',
            password='Password123!',
            role='tenant',
            phone='+254711000003'
        )
        self.token_tenant = str(RefreshToken.for_user(self.tenant).access_token)

        # Admin / Staff
        self.admin_user = User.objects.create_user(
            username='staffadmin',
            email='admin@example.com',
            password='Password123!',
            role='tenant',
            is_staff=True,
            is_superuser=True
        )
        self.token_admin = str(RefreshToken.for_user(self.admin_user).access_token)

        # Existing property owned by Landlord 1
        self.prop1 = Property.objects.create(
            landlord=self.landlord1,
            title='Bedsitter near Pwani University',
            description='Affordable bedsitter in Kilifi.',
            location='Mnarani, Kilifi, Kenya',
            latitude=Decimal('-3.626812'),
            longitude=Decimal('39.850127'),
            rent_amount=5000.00,
            bedrooms=1,
            bathrooms=1,
            property_type='bedsitter',
            status='available'
        )
        self.prop1_detail_url = reverse('property-detail', kwargs={'pk': self.prop1.pk})

    def test_tenant_cannot_create_property(self):
        self.client.credentials(HTTP_AUTHORIZATION=f'Bearer {self.token_tenant}')
        payload = {
            'title': 'Tenant Unauthorized Listing',
            'description': 'Should fail',
            'latitude': -3.626812,
            'longitude': 39.850127,
            'rent_amount': 4000.00,
            'bedrooms': 1,
            'bathrooms': 1,
            'property_type': 'single',
            'status': 'available'
        }
        response = self.client.post(self.properties_url, payload, format='json')
        self.assertEqual(response.status_code, status.HTTP_403_FORBIDDEN)

    @patch('properties.serializers.reverse_geocode')
    def test_landlord_can_create_property_with_geocoded_location(self, mock_reverse_geocode):
        mock_reverse_geocode.return_value = 'Mkwajuni, Kilifi, Kenya'
        self.client.credentials(HTTP_AUTHORIZATION=f'Bearer {self.token_landlord1}')
        payload = {
            'title': 'Modern Single Room near Campus',
            'description': 'Walking distance to campus.',
            'latitude': -3.626812,
            'longitude': 39.850127,
            'location': 'Spoofed Location from Client',  # Backend must override with geocoded result
            'rent_amount': 3500.00,
            'bedrooms': 1,
            'bathrooms': 1,
            'property_type': 'single',
            'status': 'available'
        }
        response = self.client.post(self.properties_url, payload, format='json')
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        self.assertEqual(response.data['landlord']['username'], 'landlord1')
        self.assertEqual(response.data['location'], 'Mkwajuni, Kilifi, Kenya')
        mock_reverse_geocode.assert_called_once_with(Decimal('-3.626812'), Decimal('39.850127'))

    @patch('properties.serializers.reverse_geocode')
    def test_property_creation_assigns_authenticated_landlord_and_ignores_client_landlord_override(self, mock_reverse_geocode):
        mock_reverse_geocode.return_value = 'Mnarani, Kilifi, Kenya'
        self.client.credentials(HTTP_AUTHORIZATION=f'Bearer {self.token_landlord1}')
        payload = {
            'landlord': self.landlord2.id,
            'title': 'Attempted Spoofed Property',
            'description': 'Testing ownership enforcement',
            'latitude': -3.626812,
            'longitude': 39.850127,
            'rent_amount': 6000.00,
            'bedrooms': 1,
            'bathrooms': 1,
            'property_type': 'bedsitter',
            'status': 'available'
        }
        response = self.client.post(self.properties_url, payload, format='json')
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        created_property = Property.objects.get(id=response.data['id'])
        self.assertEqual(created_property.landlord, self.landlord1)

    @patch('properties.serializers.reverse_geocode')
    def test_owner_can_update_location_coordinates_and_triggers_geocoding(self, mock_reverse_geocode):
        mock_reverse_geocode.return_value = 'Sokoni, Kilifi, Kenya'
        self.client.credentials(HTTP_AUTHORIZATION=f'Bearer {self.token_landlord1}')
        new_coords = {
            'latitude': -3.630000,
            'longitude': 39.860000
        }
        response = self.client.patch(self.prop1_detail_url, new_coords, format='json')
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.prop1.refresh_from_db()
        self.assertEqual(self.prop1.latitude, Decimal('-3.630000'))
        self.assertEqual(self.prop1.longitude, Decimal('39.860000'))
        self.assertEqual(self.prop1.location, 'Sokoni, Kilifi, Kenya')
        mock_reverse_geocode.assert_called_once_with(Decimal('-3.630000'), Decimal('39.860000'))

    @patch('properties.serializers.reverse_geocode')
    def test_unchanged_coordinates_do_not_trigger_reverse_geocoding(self, mock_reverse_geocode):
        self.client.credentials(HTTP_AUTHORIZATION=f'Bearer {self.token_landlord1}')
        # Update only rent amount (coordinates not sent)
        response = self.client.patch(self.prop1_detail_url, {'rent_amount': 5500.00}, format='json')
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.prop1.refresh_from_db()
        self.assertEqual(self.prop1.rent_amount, Decimal('5500.00'))
        mock_reverse_geocode.assert_not_called()

        # Update sending the exact same coordinates
        same_coords = {
            'latitude': -3.626812,
            'longitude': 39.850127,
            'rent_amount': 5600.00
        }
        response = self.client.patch(self.prop1_detail_url, same_coords, format='json')
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        mock_reverse_geocode.assert_not_called()

    @patch('properties.serializers.reverse_geocode')
    def test_read_operations_never_trigger_reverse_geocoding(self, mock_reverse_geocode):
        # List properties
        response = self.client.get(self.properties_url)
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        # Retrieve single property
        response = self.client.get(self.prop1_detail_url)
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        mock_reverse_geocode.assert_not_called()

    def test_landlord_cannot_edit_another_landlord_property(self):
        self.client.credentials(HTTP_AUTHORIZATION=f'Bearer {self.token_landlord2}')
        response = self.client.patch(self.prop1_detail_url, {'rent_amount': 2000.00}, format='json')
        self.assertEqual(response.status_code, status.HTTP_403_FORBIDDEN)
        self.prop1.refresh_from_db()
        self.assertEqual(self.prop1.rent_amount, Decimal('5000.00'))

    def test_staff_admin_can_manage_any_property(self):
        self.client.credentials(HTTP_AUTHORIZATION=f'Bearer {self.token_admin}')
        response = self.client.patch(self.prop1_detail_url, {'status': 'maintenance'}, format='json')
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.prop1.refresh_from_db()
        self.assertEqual(self.prop1.status, 'maintenance')

    def test_public_property_serializer_does_not_leak_contact_info(self):
        client = APIClient()
        response = client.get(self.prop1_detail_url)
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        landlord_data = response.data.get('landlord', {})
        self.assertEqual(landlord_data.get('username'), 'landlord1')
        self.assertNotIn('email', landlord_data)
        self.assertNotIn('phone', landlord_data)
        self.assertNotIn('password', landlord_data)
        self.assertIn('latitude', response.data)
        self.assertIn('longitude', response.data)
