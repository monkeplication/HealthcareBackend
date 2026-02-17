"""
Comprehensive test suite for the Healthcare Backend API.

Run with: pytest tests/ -v
"""
import pytest
from django.urls import reverse
from rest_framework import status
from rest_framework.test import APIClient
from django.contrib.auth import get_user_model

User = get_user_model()


# ===========================================================================
# Fixtures
# ===========================================================================

@pytest.fixture
def api_client():
    """Return an API client."""
    return APIClient()


@pytest.fixture
def create_user(db):
    """Factory fixture to create users."""
    def _create_user(email='test@example.com', name='Test User', password='TestPass123!'):
        return User.objects.create_user(email=email, name=name, password=password)
    return _create_user


@pytest.fixture
def user(create_user):
    """Create and return a test user."""
    return create_user()


@pytest.fixture
def another_user(create_user):
    """Create and return a second test user."""
    return create_user(email='another@example.com', name='Another User')


@pytest.fixture
def auth_client(api_client, user):
    """Return an authenticated API client."""
    response = api_client.post('/api/auth/login/', {
        'email': 'test@example.com',
        'password': 'TestPass123!',
    }, format='json')
    token = response.data['data']['tokens']['access']
    api_client.credentials(HTTP_AUTHORIZATION=f'Bearer {token}')
    return api_client


@pytest.fixture
def patient_data():
    """Return sample patient data."""
    return {
        'first_name': 'John',
        'last_name': 'Doe',
        'email': 'john.doe@example.com',
        'phone': '1234567890',
        'date_of_birth': '1990-01-15',
        'gender': 'M',
        'blood_group': 'O+',
    }


@pytest.fixture
def doctor_data():
    """Return sample doctor data."""
    return {
        'first_name': 'Jane',
        'last_name': 'Smith',
        'email': 'dr.jane.smith@hospital.com',
        'phone': '9876543210',
        'specialization': 'cardiology',
        'license_number': 'LIC-2024-001',
        'years_of_experience': 10,
    }


# ===========================================================================
# Authentication Tests
# ===========================================================================

@pytest.mark.django_db
class TestUserRegistration:
    """Tests for POST /api/auth/register/"""

    def test_register_success(self, api_client):
        """Test successful user registration."""
        data = {
            'name': 'New User',
            'email': 'newuser@example.com',
            'password': 'SecurePass123!',
            'confirm_password': 'SecurePass123!',
        }
        response = api_client.post('/api/auth/register/', data, format='json')

        assert response.status_code == status.HTTP_201_CREATED
        assert response.data['success'] is True
        assert 'tokens' in response.data['data']
        assert 'user' in response.data['data']
        assert response.data['data']['user']['email'] == 'newuser@example.com'

    def test_register_duplicate_email(self, api_client, user):
        """Test registration with duplicate email fails."""
        data = {
            'name': 'Duplicate User',
            'email': 'test@example.com',  # already exists
            'password': 'SecurePass123!',
            'confirm_password': 'SecurePass123!',
        }
        response = api_client.post('/api/auth/register/', data, format='json')

        assert response.status_code == status.HTTP_400_BAD_REQUEST
        assert response.data['success'] is False

    def test_register_password_mismatch(self, api_client):
        """Test registration with mismatched passwords fails."""
        data = {
            'name': 'Test User',
            'email': 'test2@example.com',
            'password': 'SecurePass123!',
            'confirm_password': 'DifferentPass123!',
        }
        response = api_client.post('/api/auth/register/', data, format='json')

        assert response.status_code == status.HTTP_400_BAD_REQUEST
        assert 'confirm_password' in str(response.data.get('errors', ''))

    def test_register_missing_fields(self, api_client):
        """Test registration with missing required fields fails."""
        response = api_client.post('/api/auth/register/', {}, format='json')
        assert response.status_code == status.HTTP_400_BAD_REQUEST

    def test_register_weak_password(self, api_client):
        """Test registration with weak password fails."""
        data = {
            'name': 'Test User',
            'email': 'test3@example.com',
            'password': '123',
            'confirm_password': '123',
        }
        response = api_client.post('/api/auth/register/', data, format='json')
        assert response.status_code == status.HTTP_400_BAD_REQUEST


@pytest.mark.django_db
class TestUserLogin:
    """Tests for POST /api/auth/login/"""

    def test_login_success(self, api_client, user):
        """Test successful login returns tokens."""
        data = {
            'email': 'test@example.com',
            'password': 'TestPass123!',
        }
        response = api_client.post('/api/auth/login/', data, format='json')

        assert response.status_code == status.HTTP_200_OK
        assert response.data['success'] is True
        assert 'access' in response.data['data']['tokens']
        assert 'refresh' in response.data['data']['tokens']

    def test_login_wrong_password(self, api_client, user):
        """Test login with wrong password fails."""
        data = {
            'email': 'test@example.com',
            'password': 'WrongPassword!',
        }
        response = api_client.post('/api/auth/login/', data, format='json')
        assert response.status_code == status.HTTP_401_UNAUTHORIZED

    def test_login_nonexistent_user(self, api_client):
        """Test login with non-existent email fails."""
        data = {
            'email': 'nobody@example.com',
            'password': 'SomePass123!',
        }
        response = api_client.post('/api/auth/login/', data, format='json')
        assert response.status_code == status.HTTP_401_UNAUTHORIZED

    def test_unauthenticated_access_denied(self, api_client):
        """Test that protected endpoints require authentication."""
        response = api_client.get('/api/patients/')
        assert response.status_code == status.HTTP_401_UNAUTHORIZED


# ===========================================================================
# Patient Tests
# ===========================================================================

@pytest.mark.django_db
class TestPatientCRUD:
    """Tests for patient management endpoints."""

    def test_create_patient(self, auth_client, patient_data):
        """Test creating a new patient."""
        response = auth_client.post('/api/patients/', patient_data, format='json')

        assert response.status_code == status.HTTP_201_CREATED
        assert response.data['success'] is True
        assert response.data['data']['first_name'] == 'John'
        assert response.data['data']['last_name'] == 'Doe'

    def test_list_patients(self, auth_client, patient_data):
        """Test listing patients returns only user's patients."""
        # Create a patient first
        auth_client.post('/api/patients/', patient_data, format='json')

        response = auth_client.get('/api/patients/')
        assert response.status_code == status.HTTP_200_OK
        assert response.data['success'] is True
        assert response.data['count'] >= 1

    def test_get_patient_detail(self, auth_client, patient_data):
        """Test retrieving a specific patient."""
        create_response = auth_client.post('/api/patients/', patient_data, format='json')
        patient_id = create_response.data['data']['id']

        response = auth_client.get(f'/api/patients/{patient_id}/')
        assert response.status_code == status.HTTP_200_OK
        assert response.data['data']['id'] == patient_id

    def test_update_patient(self, auth_client, patient_data):
        """Test updating patient information."""
        create_response = auth_client.post('/api/patients/', patient_data, format='json')
        patient_id = create_response.data['data']['id']

        updated_data = {**patient_data, 'first_name': 'Updated'}
        response = auth_client.put(f'/api/patients/{patient_id}/', updated_data, format='json')

        assert response.status_code == status.HTTP_200_OK
        assert response.data['data']['first_name'] == 'Updated'

    def test_delete_patient(self, auth_client, patient_data):
        """Test deleting a patient record."""
        create_response = auth_client.post('/api/patients/', patient_data, format='json')
        patient_id = create_response.data['data']['id']

        response = auth_client.delete(f'/api/patients/{patient_id}/')
        assert response.status_code == status.HTTP_200_OK

        # Verify deletion
        get_response = auth_client.get(f'/api/patients/{patient_id}/')
        assert get_response.status_code == status.HTTP_404_NOT_FOUND

    def test_patient_isolation(self, api_client, create_user, patient_data):
        """Test that users can only see their own patients."""
        # User 1 logs in and creates a patient
        user1 = create_user(email='user1@example.com', name='User One')
        api_client.post('/api/auth/login/', {'email': 'user1@example.com', 'password': 'TestPass123!'})
        login_response = api_client.post('/api/auth/login/', {
            'email': 'user1@example.com',
            'password': 'TestPass123!'
        }, format='json')
        token1 = login_response.data['data']['tokens']['access']
        api_client.credentials(HTTP_AUTHORIZATION=f'Bearer {token1}')
        api_client.post('/api/patients/', patient_data, format='json')

        # User 2 logs in and should NOT see User 1's patient
        user2 = create_user(email='user2@example.com', name='User Two')
        login_response2 = api_client.post('/api/auth/login/', {
            'email': 'user2@example.com',
            'password': 'TestPass123!'
        }, format='json')
        token2 = login_response2.data['data']['tokens']['access']
        api_client.credentials(HTTP_AUTHORIZATION=f'Bearer {token2}')

        response = api_client.get('/api/patients/')
        assert response.data['count'] == 0


# ===========================================================================
# Doctor Tests
# ===========================================================================

@pytest.mark.django_db
class TestDoctorCRUD:
    """Tests for doctor management endpoints."""

    def test_create_doctor(self, auth_client, doctor_data):
        """Test creating a new doctor."""
        response = auth_client.post('/api/doctors/', doctor_data, format='json')

        assert response.status_code == status.HTTP_201_CREATED
        assert response.data['success'] is True
        assert response.data['data']['email'] == 'dr.jane.smith@hospital.com'

    def test_list_doctors(self, auth_client, doctor_data):
        """Test listing all doctors."""
        auth_client.post('/api/doctors/', doctor_data, format='json')

        response = auth_client.get('/api/doctors/')
        assert response.status_code == status.HTTP_200_OK
        assert response.data['count'] >= 1

    def test_duplicate_license_fails(self, auth_client, doctor_data):
        """Test that duplicate license numbers are rejected."""
        auth_client.post('/api/doctors/', doctor_data, format='json')

        # Try creating another doctor with same license
        doctor_data2 = {**doctor_data, 'email': 'other@doctor.com'}
        response = auth_client.post('/api/doctors/', doctor_data2, format='json')
        assert response.status_code == status.HTTP_400_BAD_REQUEST

    def test_filter_doctors_by_specialization(self, auth_client, doctor_data):
        """Test filtering doctors by specialization."""
        auth_client.post('/api/doctors/', doctor_data, format='json')

        response = auth_client.get('/api/doctors/?specialization=cardiology')
        assert response.status_code == status.HTTP_200_OK
        for doc in response.data['data']:
            assert doc['specialization'] == 'cardiology'


# ===========================================================================
# Mapping Tests
# ===========================================================================

@pytest.mark.django_db
class TestPatientDoctorMapping:
    """Tests for patient-doctor mapping endpoints."""

    def _create_patient(self, auth_client, patient_data):
        r = auth_client.post('/api/patients/', patient_data, format='json')
        return r.data['data']['id']

    def _create_doctor(self, auth_client, doctor_data):
        r = auth_client.post('/api/doctors/', doctor_data, format='json')
        return r.data['data']['id']

    def test_assign_doctor_to_patient(self, auth_client, patient_data, doctor_data):
        """Test assigning a doctor to a patient."""
        patient_id = self._create_patient(auth_client, patient_data)
        doctor_id = self._create_doctor(auth_client, doctor_data)

        mapping_data = {'patient': patient_id, 'doctor': doctor_id}
        response = auth_client.post('/api/mappings/', mapping_data, format='json')

        assert response.status_code == status.HTTP_201_CREATED
        assert response.data['success'] is True

    def test_list_all_mappings(self, auth_client, patient_data, doctor_data):
        """Test listing all mappings."""
        patient_id = self._create_patient(auth_client, patient_data)
        doctor_id = self._create_doctor(auth_client, doctor_data)
        auth_client.post('/api/mappings/', {'patient': patient_id, 'doctor': doctor_id}, format='json')

        response = auth_client.get('/api/mappings/')
        assert response.status_code == status.HTTP_200_OK
        assert response.data['count'] >= 1

    def test_get_patient_doctors(self, auth_client, patient_data, doctor_data):
        """Test getting all doctors for a specific patient."""
        patient_id = self._create_patient(auth_client, patient_data)
        doctor_id = self._create_doctor(auth_client, doctor_data)
        auth_client.post('/api/mappings/', {'patient': patient_id, 'doctor': doctor_id}, format='json')

        response = auth_client.get(f'/api/mappings/{patient_id}/')
        assert response.status_code == status.HTTP_200_OK
        assert response.data['patient']['id'] == patient_id
        assert response.data['count'] == 1

    def test_duplicate_mapping_fails(self, auth_client, patient_data, doctor_data):
        """Test that duplicate mappings are rejected."""
        patient_id = self._create_patient(auth_client, patient_data)
        doctor_id = self._create_doctor(auth_client, doctor_data)

        mapping_data = {'patient': patient_id, 'doctor': doctor_id}
        auth_client.post('/api/mappings/', mapping_data, format='json')

        # Try duplicate
        response = auth_client.post('/api/mappings/', mapping_data, format='json')
        assert response.status_code == status.HTTP_400_BAD_REQUEST

    def test_delete_mapping(self, auth_client, patient_data, doctor_data):
        """Test removing a doctor from a patient."""
        patient_id = self._create_patient(auth_client, patient_data)
        doctor_id = self._create_doctor(auth_client, doctor_data)

        create_response = auth_client.post(
            '/api/mappings/', {'patient': patient_id, 'doctor': doctor_id}, format='json'
        )
        mapping_id = create_response.data['data']['id']

        response = auth_client.delete(f'/api/mappings/detail/{mapping_id}/')
        assert response.status_code == status.HTTP_200_OK

        # Verify it's gone
        patient_response = auth_client.get(f'/api/mappings/{patient_id}/')
        assert patient_response.data['count'] == 0
