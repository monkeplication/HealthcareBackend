# Healthcare Backend API

A secure, production-ready Django REST Framework backend for managing patient and doctor records with JWT authentication.

---

## Tech Stack

| Layer | Technology |
|-------|------------|
| Framework | Django 4.2 + Django REST Framework |
| Database | PostgreSQL |
| Authentication | JWT via `djangorestframework-simplejwt` |
| Containerization | Docker + Docker Compose |
| Testing | pytest + pytest-django |

---

## Project Structure

```
healthcare_backend/
├── manage.py
├── requirements.txt
├── .env.example               ← Copy to .env and configure
├── docker-compose.yml
├── Dockerfile
├── pytest.ini
│
├── healthcare_backend/        ← Django project config
│   ├── settings.py
│   ├── urls.py
│   ├── exceptions.py          ← Custom error responses
│   └── wsgi.py
│
├── apps/
│   ├── authentication/        ← Custom user model + JWT
│   │   ├── models.py
│   │   ├── serializers.py
│   │   ├── views.py
│   │   └── urls.py
│   │
│   ├── patients/              ← Patient CRUD
│   │   ├── models.py
│   │   ├── serializers.py
│   │   ├── views.py
│   │   └── urls.py
│   │
│   ├── doctors/               ← Doctor CRUD
│   │   ├── models.py
│   │   ├── serializers.py
│   │   ├── views.py
│   │   └── urls.py
│   │
│   └── mappings/              ← Patient-Doctor assignments
│       ├── models.py
│       ├── serializers.py
│       ├── views.py
│       └── urls.py
│
└── tests/
    └── test_api.py            ← Full test suite
```

---

## Quick Start

### Option A: Docker (Recommended)

```bash
# 1. Clone and enter directory
git clone <your-repo>
cd healthcare_backend

# 2. Configure environment
cp .env.example .env
# Edit .env with your values

# 3. Start services
docker-compose up --build

# 4. Run migrations (first time only — handled automatically by docker-compose)
docker-compose exec web python manage.py migrate

# 5. Create superuser (optional)
docker-compose exec web python manage.py createsuperuser
```

API available at: **http://localhost:8000**

---

### Option B: Local Setup

```bash
# 1. Create and activate virtual environment
python -m venv venv
source venv/bin/activate      # Windows: venv\Scripts\activate

# 2. Install dependencies
pip install -r requirements.txt

# 3. Configure environment
cp .env.example .env
# Edit .env with your PostgreSQL credentials

# 4. Create PostgreSQL database
psql -U postgres
CREATE DATABASE healthcare_db;
\q

# 5. Run migrations
python manage.py migrate

# 6. Start development server
python manage.py runserver
```

---

## Environment Variables

| Variable | Description | Default |
|----------|-------------|---------|
| `SECRET_KEY` | Django secret key | (insecure dev key) |
| `DEBUG` | Debug mode | `True` |
| `ALLOWED_HOSTS` | Allowed hosts (comma-separated) | `localhost,127.0.0.1` |
| `DB_NAME` | PostgreSQL database name | `healthcare_db` |
| `DB_USER` | PostgreSQL username | `postgres` |
| `DB_PASSWORD` | PostgreSQL password | `postgres` |
| `DB_HOST` | PostgreSQL host | `localhost` |
| `DB_PORT` | PostgreSQL port | `5432` |
| `JWT_ACCESS_TOKEN_LIFETIME_MINUTES` | JWT access token TTL (minutes) | `60` |
| `JWT_REFRESH_TOKEN_LIFETIME_DAYS` | JWT refresh token TTL (days) | `7` |
| `CORS_ALLOWED_ORIGINS` | Allowed CORS origins (comma-separated) | `http://localhost:3000` |

---

## API Reference

All protected endpoints require the header:
```
Authorization: Bearer <access_token>
```

All responses follow this consistent structure:
```json
{
  "success": true,
  "message": "Human-readable message",
  "data": { ... }
}
```

Error responses:
```json
{
  "success": false,
  "message": "What went wrong",
  "errors": { "field": ["error detail"] }
}
```

---

### 1. Authentication APIs

#### `POST /api/auth/register/`
Register a new user.

**Request Body:**
```json
{
  "name": "Dr. Alice Johnson",
  "email": "alice@hospital.com",
  "password": "SecurePass123!",
  "confirm_password": "SecurePass123!"
}
```

**Response `201`:**
```json
{
  "success": true,
  "message": "User registered successfully.",
  "data": {
    "user": {
      "id": 1,
      "name": "Dr. Alice Johnson",
      "email": "alice@hospital.com",
      "created_at": "2024-01-15T10:30:00Z"
    },
    "tokens": {
      "access": "eyJ0...",
      "refresh": "eyJ1..."
    }
  }
}
```

---

#### `POST /api/auth/login/`
Authenticate user and receive JWT tokens.

**Request Body:**
```json
{
  "email": "alice@hospital.com",
  "password": "SecurePass123!"
}
```

**Response `200`:**
```json
{
  "success": true,
  "message": "Login successful.",
  "data": {
    "user": { "id": 1, "name": "Dr. Alice Johnson", "email": "alice@hospital.com" },
    "tokens": {
      "access": "eyJ0...",
      "refresh": "eyJ1..."
    }
  }
}
```

---

#### `POST /api/auth/logout/`  🔒
Invalidate the refresh token.

**Request Body:**
```json
{ "refresh": "eyJ1..." }
```

---

#### `POST /api/auth/token/refresh/`
Get a new access token using a refresh token.

**Request Body:**
```json
{ "refresh": "eyJ1..." }
```

---

#### `GET /api/auth/me/`  🔒
Get the current user's profile.

---

### 2. Patient Management APIs  🔒

All patient endpoints require authentication. Patients are scoped to the authenticated user.

---

#### `POST /api/patients/`
Create a new patient record.

**Request Body:**
```json
{
  "first_name": "John",
  "last_name": "Doe",
  "email": "john.doe@email.com",
  "phone": "555-1234",
  "date_of_birth": "1985-06-15",
  "gender": "M",
  "blood_group": "O+",
  "allergies": "Penicillin",
  "medical_history": "Hypertension diagnosed 2020",
  "current_medications": "Lisinopril 10mg",
  "emergency_contact_name": "Jane Doe",
  "emergency_contact_phone": "555-5678",
  "address": "123 Main St",
  "city": "Chicago",
  "state": "IL",
  "country": "USA"
}
```

**Gender choices:** `M` (Male), `F` (Female), `O` (Other), `N` (Prefer not to say)

**Blood group choices:** `A+`, `A-`, `B+`, `B-`, `AB+`, `AB-`, `O+`, `O-`

---

#### `GET /api/patients/`
List all patients created by the authenticated user.

**Query Parameters:**
- `search` — Filter by name or email
- `gender` — Filter by gender code

---

#### `GET /api/patients/<id>/`
Retrieve a specific patient's full details.

---

#### `PUT /api/patients/<id>/`
Replace all patient fields (full update).

---

#### `PATCH /api/patients/<id>/`
Update specific patient fields (partial update).

---

#### `DELETE /api/patients/<id>/`
Permanently delete a patient record.

---

### 3. Doctor Management APIs  🔒

---

#### `POST /api/doctors/`
Add a new doctor.

**Request Body:**
```json
{
  "first_name": "Emily",
  "last_name": "Chen",
  "email": "dr.emily@hospital.com",
  "phone": "555-9876",
  "specialization": "neurology",
  "license_number": "LIC-2024-007",
  "years_of_experience": 15,
  "qualification": "MD, PhD Neuroscience",
  "bio": "Board-certified neurologist specializing in epilepsy treatment.",
  "consultation_fee": "250.00",
  "is_available": true,
  "hospital_name": "City Medical Center",
  "city": "San Francisco",
  "state": "CA",
  "country": "USA"
}
```

**Specialization choices:**
`general`, `cardiology`, `dermatology`, `endocrinology`, `gastroenterology`,
`hematology`, `infectious_disease`, `internal_medicine`, `nephrology`,
`neurology`, `obstetrics_gynecology`, `oncology`, `ophthalmology`,
`orthopedics`, `pediatrics`, `psychiatry`, `pulmonology`, `radiology`,
`rheumatology`, `surgery`, `urology`, `other`

---

#### `GET /api/doctors/`
Retrieve all doctors. All authenticated users can see all doctors.

**Query Parameters:**
- `search` — Filter by name or hospital
- `specialization` — Filter by specialization code
- `is_available` — `true` or `false`
- `city` — Filter by city name

---

#### `GET /api/doctors/<id>/`
Get a specific doctor's full details.

---

#### `PUT /api/doctors/<id>/`
Full update of a doctor record.

---

#### `PATCH /api/doctors/<id>/`
Partial update of a doctor record.

---

#### `DELETE /api/doctors/<id>/`
Delete a doctor record.

---

### 4. Patient-Doctor Mapping APIs  🔒

---

#### `POST /api/mappings/`
Assign a doctor to a patient.

**Request Body:**
```json
{
  "patient": 1,
  "doctor": 3,
  "is_primary": true,
  "notes": "Referred for cardiac evaluation"
}
```

---

#### `GET /api/mappings/`
Retrieve all patient-doctor mappings.

**Query Parameters:**
- `patient_id` — Filter by patient ID
- `doctor_id` — Filter by doctor ID
- `is_primary` — `true` or `false`

---

#### `GET /api/mappings/<patient_id>/`
Get all doctors assigned to a specific patient.

**Response:**
```json
{
  "success": true,
  "patient": { "id": 1, "full_name": "John Doe" },
  "count": 2,
  "data": [
    {
      "id": 1,
      "doctor": 3,
      "doctor_detail": { "id": 3, "display_name": "Dr. Emily Chen", ... },
      "is_primary": true,
      "notes": "Primary care physician",
      "assigned_at": "2024-01-15T10:30:00Z"
    }
  ]
}
```

---

#### `DELETE /api/mappings/detail/<id>/`
Remove a specific patient-doctor mapping by mapping ID.

---

## Running Tests

```bash
# Install test dependencies
pip install pytest pytest-django

# Run all tests
pytest tests/ -v

# Run specific test class
pytest tests/test_api.py::TestPatientCRUD -v

# Run with coverage
pip install pytest-cov
pytest tests/ --cov=apps --cov-report=html
```

---

## Admin Interface

Access the Django Admin at **http://localhost:8000/admin/**

Create a superuser:
```bash
python manage.py createsuperuser
```

---

## Security Highlights

- **JWT Tokens** — Short-lived access tokens (60 min) with rotatable refresh tokens
- **Token Blacklisting** — Refresh tokens are blacklisted on logout
- **Password Validation** — Enforces Django's built-in password strength validators
- **Data Isolation** — Patients are scoped per user; users cannot access others' records
- **Environment Variables** — All secrets and credentials loaded from `.env`
- **CORS Protection** — Only whitelisted origins allowed

---

## Postman Collection

Import these sample requests into Postman:

1. **Register** → `POST http://localhost:8000/api/auth/register/`
2. **Login** → `POST http://localhost:8000/api/auth/login/`  
   *Copy the `access` token from the response*
3. Set **Bearer Token** in Authorization header for all subsequent requests
4. **Create Patient** → `POST http://localhost:8000/api/patients/`
5. **Create Doctor** → `POST http://localhost:8000/api/doctors/`
6. **Assign Doctor** → `POST http://localhost:8000/api/mappings/`
7. **Get Patient's Doctors** → `GET http://localhost:8000/api/mappings/{patient_id}/`
