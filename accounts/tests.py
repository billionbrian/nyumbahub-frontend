from django.test import TestCase
from django.urls import reverse
from rest_framework.test import APIClient
from rest_framework import status
from django.contrib.auth import get_user_model
from rest_framework_simplejwt.tokens import RefreshToken

User = get_user_model()


class AccountsAuthTests(TestCase):
    def setUp(self):
        self.client = APIClient()
        self.signup_url = reverse('signup')
        self.login_url = reverse('login')
        self.me_url = reverse('current_user')
        self.refresh_url = reverse('token_refresh')
        self.logout_url = reverse('logout')

        # Existing base user
        self.existing_user = User.objects.create_user(
            username='existinguser',
            email='existing@example.com',
            password='ExistingPassword123!',
            role='tenant',
            phone='+254711111111'
        )

    # ==========================
    # 1. SIGNUP TESTS
    # ==========================
    def test_tenant_signup_success(self):
        payload = {
            'username': 'newtenant',
            'email': 'tenant@example.com',
            'password': 'SecurePassword123!',
            'role': 'tenant',
            'phone': '+254700112233',
            'first_name': 'New',
            'last_name': 'Tenant'
        }
        response = self.client.post(self.signup_url, payload, format='json')
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        self.assertIn('Account created successfully', response.data['message'])

        user = User.objects.get(username='newtenant')
        self.assertEqual(user.role, 'tenant')
        self.assertEqual(user.email, 'tenant@example.com')
        self.assertFalse(user.is_staff)
        self.assertFalse(user.is_superuser)
        self.assertTrue(user.is_active)
        self.assertFalse(user.email_verified)
        self.assertTrue(user.check_password('SecurePassword123!'))

    def test_landlord_signup_success(self):
        payload = {
            'username': 'newlandlord',
            'email': 'landlord@example.com',
            'password': 'SecurePassword123!',
            'role': 'landlord',
            'phone': '+254722334455'
        }
        response = self.client.post(self.signup_url, payload, format='json')
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)

        user = User.objects.get(username='newlandlord')
        self.assertEqual(user.role, 'landlord')
        self.assertFalse(user.is_staff)
        self.assertFalse(user.is_superuser)

    def test_duplicate_username_rejected(self):
        payload = {
            'username': 'existinguser',
            'email': 'different@example.com',
            'password': 'SecurePassword123!',
            'role': 'tenant'
        }
        response = self.client.post(self.signup_url, payload, format='json')
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
        self.assertIn('username', response.data)

    def test_duplicate_email_rejected(self):
        payload = {
            'username': 'uniquename',
            'email': 'existing@example.com',
            'password': 'SecurePassword123!',
            'role': 'tenant'
        }
        response = self.client.post(self.signup_url, payload, format='json')
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
        self.assertIn('email', response.data)

    def test_case_insensitive_duplicate_email_rejected(self):
        payload = {
            'username': 'uniquename2',
            'email': 'EXISTING@EXAMPLE.COM',
            'password': 'SecurePassword123!',
            'role': 'tenant'
        }
        response = self.client.post(self.signup_url, payload, format='json')
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
        self.assertIn('email', response.data)

    def test_invalid_role_rejected(self):
        payload = {
            'username': 'badroleuser',
            'email': 'badrole@example.com',
            'password': 'SecurePassword123!',
            'role': 'admin'
        }
        response = self.client.post(self.signup_url, payload, format='json')
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
        self.assertIn('role', response.data)

    def test_privilege_escalation_ignored(self):
        payload = {
            'username': 'hackeruser',
            'email': 'hacker@example.com',
            'password': 'SecurePassword123!',
            'role': 'landlord',
            'is_staff': True,
            'is_superuser': True
        }
        response = self.client.post(self.signup_url, payload, format='json')
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)

        user = User.objects.get(username='hackeruser')
        self.assertFalse(user.is_staff)
        self.assertFalse(user.is_superuser)

    def test_weak_password_rejected(self):
        payload = {
            'username': 'weakpassuser',
            'email': 'weakpass@example.com',
            'password': '123',
            'role': 'tenant'
        }
        response = self.client.post(self.signup_url, payload, format='json')
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
        self.assertIn('password', response.data)

    def test_legacy_name_field_handled(self):
        payload = {
            'name': 'Legacy Student',
            'email': 'legacy@example.com',
            'password': 'SecurePassword123!',
            'role': 'tenant'
        }
        response = self.client.post(self.signup_url, payload, format='json')
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        user = User.objects.get(email='legacy@example.com')
        self.assertEqual(user.username, 'Legacy Student')
        self.assertEqual(user.first_name, 'Legacy')
        self.assertEqual(user.last_name, 'Student')

    # ==========================
    # 2. LOGIN & TOKEN TESTS
    # ==========================
    def test_tenant_login_success(self):
        payload = {
            'username': 'existinguser',
            'password': 'ExistingPassword123!'
        }
        response = self.client.post(self.login_url, payload, format='json')
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertIn('token', response.data)
        self.assertIn('access', response.data)
        self.assertIn('refresh', response.data)
        self.assertEqual(response.data['user']['username'], 'existinguser')
        self.assertEqual(response.data['user']['role'], 'tenant')

    def test_login_with_email_success(self):
        payload = {
            'username': 'EXISTING@EXAMPLE.COM',
            'password': 'ExistingPassword123!'
        }
        response = self.client.post(self.login_url, payload, format='json')
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertIn('token', response.data)
        self.assertEqual(response.data['user']['username'], 'existinguser')

    def test_unverified_email_login_allowed_for_now(self):
        # Email verified = False must still be able to log in at this stage
        unverified_user = User.objects.create_user(
            username='unverified',
            email='unverified@example.com',
            password='SecurePassword123!',
            role='tenant',
            email_verified=False
        )
        payload = {
            'username': 'unverified',
            'password': 'SecurePassword123!'
        }
        response = self.client.post(self.login_url, payload, format='json')
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertIn('token', response.data)

    def test_login_invalid_password(self):
        payload = {
            'username': 'existinguser',
            'password': 'WrongPassword!'
        }
        response = self.client.post(self.login_url, payload, format='json')
        self.assertEqual(response.status_code, status.HTTP_401_UNAUTHORIZED)

    # ==========================
    # 3. CURRENT USER (/me/) TESTS
    # ==========================
    def test_me_with_valid_token(self):
        refresh = RefreshToken.for_user(self.existing_user)
        self.client.credentials(HTTP_AUTHORIZATION=f'Bearer {str(refresh.access_token)}')
        response = self.client.get(self.me_url)
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.data['username'], 'existinguser')
        self.assertEqual(response.data['email'], 'existing@example.com')
        self.assertEqual(response.data['role'], 'tenant')
        self.assertNotIn('password', response.data)

    def test_me_without_token(self):
        response = self.client.get(self.me_url)
        self.assertEqual(response.status_code, status.HTTP_401_UNAUTHORIZED)

    def test_me_with_invalid_token(self):
        self.client.credentials(HTTP_AUTHORIZATION='Bearer invalidtokenxyz')
        response = self.client.get(self.me_url)
        self.assertEqual(response.status_code, status.HTTP_401_UNAUTHORIZED)

    # ==========================
    # 4. REFRESH & LOGOUT TESTS
    # ==========================
    def test_token_refresh(self):
        refresh = RefreshToken.for_user(self.existing_user)
        payload = {'refresh': str(refresh)}
        response = self.client.post(self.refresh_url, payload, format='json')
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertIn('access', response.data)

    def test_logout_blacklists_refresh_token(self):
        refresh = RefreshToken.for_user(self.existing_user)
        refresh_str = str(refresh)
        self.client.credentials(HTTP_AUTHORIZATION=f'Bearer {str(refresh.access_token)}')

        # Logout
        response = self.client.post(self.logout_url, {'refresh': refresh_str}, format='json')
        self.assertEqual(response.status_code, status.HTTP_200_OK)

        # Attempt to use blacklisted refresh token to obtain a new access token
        refresh_response = self.client.post(self.refresh_url, {'refresh': refresh_str}, format='json')
        self.assertEqual(refresh_response.status_code, status.HTTP_401_UNAUTHORIZED)
