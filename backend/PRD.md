# Backend PRD - Administrator Panel Backend System

## 1. Loyiha Umumiy Ma'lumotlari

### 1.1 Loyiha Nomi
**Administrator Panel Backend System** - Tashkilotlar va foydalanuvchilarni boshqarish tizimi

### 1.2 Loyiha Tavsifi
Bu loyiha restoran, kafe va boshqa oziq-ovqat korxonalarini boshqarish uchun administrator panelining backend qismi hisoblanadi. Tizim tashkilotlar, foydalanuvchilar, to'lovlar, tariflar va qurilmalarni boshqarish imkoniyatlarini taqdim etadi.

### 1.3 Asosiy Maqsadlar
- Tashkilotlar va ularning filiallarini boshqarish
- Foydalanuvchilar va ularning ulushlarini boshqarish
- To'lovlar va hisob-kitoblarni kuzatish
- Tariflar va qo'shimcha xizmatlarni boshqarish
- Qurilmalar va ularning holatini kuzatish
- Xavfsiz autentifikatsiya va avtorizatsiya

## 2. Texnik Talablar

### 2.1 Texnologiyalar
- **Backend Framework**: FastAPI (Python 3.11+)
- **Database**: PostgreSQL 15+
- **ORM**: SQLAlchemy 2.0+
- **Authentication**: JWT (JSON Web Tokens)
- **Password Hashing**: bcrypt
- **API Documentation**: OpenAPI/Swagger
- **Validation**: Pydantic
- **CORS**: FastAPI CORS middleware
- **Environment**: Railway.com (production), Local development

### 2.2 Deployment Talablari
- **Production**: Railway.com
- **Database**: PostgreSQL (Railway managed)
- **Environment Variables**: Railway environment variables
- **Local Development**: Docker Compose yoki local PostgreSQL

## 3. Database Schema

### 3.1 Users Table
```sql
CREATE TABLE users (
    id SERIAL PRIMARY KEY,
    full_name VARCHAR(255) NOT NULL,
    phone VARCHAR(20) UNIQUE NOT NULL,
    password_hash VARCHAR(255) NOT NULL,
    address TEXT,
    role VARCHAR(20) NOT NULL DEFAULT 'registrator' CHECK (role IN ('admin', 'registrator', 'moderator')),
    share_percentage DECIMAL(5,2) DEFAULT 0.00,
    is_active BOOLEAN DEFAULT TRUE,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);
```

### 3.2 Organizations Table
```sql
CREATE TABLE organizations (
    id SERIAL PRIMARY KEY,
    name VARCHAR(255) NOT NULL,
    phone VARCHAR(20) NOT NULL,
    boss VARCHAR(255) NOT NULL,
    plan VARCHAR(50) NOT NULL DEFAULT 'Free',
    registrator_id INTEGER REFERENCES users(id),
    registration_date DATE NOT NULL,
    plan_expiration_days INTEGER DEFAULT 30,
    is_active BOOLEAN DEFAULT TRUE,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);
```

### 3.3 Branches Table
```sql
CREATE TABLE branches (
    id SERIAL PRIMARY KEY,
    organization_id INTEGER REFERENCES organizations(id) ON DELETE CASCADE,
    name VARCHAR(255) NOT NULL,
    location TEXT NOT NULL,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);
```

### 3.4 Devices Table
```sql
CREATE TABLE devices (
    id VARCHAR(255) PRIMARY KEY,
    branch_id INTEGER REFERENCES branches(id) ON DELETE CASCADE,
    name VARCHAR(255) NOT NULL,
    os VARCHAR(100),
    last_seen TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    is_active BOOLEAN DEFAULT TRUE,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);
```

### 3.5 Custom Plans Table
```sql
CREATE TABLE custom_plans (
    id SERIAL PRIMARY KEY,
    name VARCHAR(100) UNIQUE NOT NULL,
    branches INTEGER DEFAULT 1,
    devices_per_branch INTEGER DEFAULT 1,
    waiters INTEGER DEFAULT 0,
    kds BOOLEAN DEFAULT FALSE,
    warehouse_control VARCHAR(20) DEFAULT 'none' CHECK (warehouse_control IN ('none', 'lite', 'pro')),
    tech_card VARCHAR(20) DEFAULT 'none' CHECK (tech_card IN ('none', 'lite', 'pro')),
    chat_support BOOLEAN DEFAULT FALSE,
    api_integrations TEXT[], -- Array of integration names
    phone_support_247 BOOLEAN DEFAULT FALSE,
    personal_manager BOOLEAN DEFAULT FALSE,
    monthly_price DECIMAL(12,2) DEFAULT 0.00,
    yearly_price DECIMAL(12,2) DEFAULT 0.00,
    flag VARCHAR(50),
    color VARCHAR(7),
    is_active BOOLEAN DEFAULT TRUE,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);
```

### 3.6 Add Ons Table
```sql
CREATE TABLE add_ons (
    id VARCHAR(255) PRIMARY KEY,
    organization_id INTEGER REFERENCES organizations(id) ON DELETE CASCADE,
    type VARCHAR(20) NOT NULL CHECK (type IN ('branch', 'device', 'waiter')),
    quantity INTEGER NOT NULL DEFAULT 1,
    monthly_price DECIMAL(12,2) NOT NULL DEFAULT 0.00,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);
```

### 3.7 Payments Table
```sql
CREATE TABLE payments (
    id SERIAL PRIMARY KEY,
    organization_id INTEGER REFERENCES organizations(id) ON DELETE CASCADE,
    amount DECIMAL(12,2) NOT NULL,
    source VARCHAR(50) NOT NULL CHECK (source IN ('Subscription', 'Click', 'Payme')),
    payment_date DATE NOT NULL,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);
```

### 3.8 User Payouts Table
```sql
CREATE TABLE user_payouts (
    id SERIAL PRIMARY KEY,
    user_id INTEGER REFERENCES users(id) ON DELETE CASCADE,
    amount DECIMAL(12,2) NOT NULL,
    source VARCHAR(20) NOT NULL CHECK (source IN ('O\'tkazma', 'Naqd pul')),
    payout_date DATE NOT NULL,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);
```

### 3.9 Registration Requests Table
```sql
CREATE TABLE registration_requests (
    id SERIAL PRIMARY KEY,
    full_name VARCHAR(255) NOT NULL,
    phone VARCHAR(20) NOT NULL,
    password VARCHAR(255) NOT NULL,
    address TEXT,
    status VARCHAR(20) DEFAULT 'pending' CHECK (status IN ('pending', 'approved', 'rejected')),
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);
```

## 4. API Endpoints

### 4.1 Authentication Endpoints

#### POST /api/auth/login
```json
{
    "phone": "901234567",
    "password": "admin123"
}
```
**Response:**
```json
{
    "access_token": "eyJ0eXAiOiJKV1QiLCJhbGciOiJIUzI1NiJ9...",
    "token_type": "bearer",
    "user": {
        "id": 1,
        "full_name": "Admin User",
        "phone": "901234567",
        "role": "admin",
        "share_percentage": 0.00
    }
}
```

#### POST /api/auth/register-request
```json
{
    "full_name": "John Doe",
    "phone": "901234567",
    "password": "password123",
    "address": "Tashkent, Uzbekistan"
}
```

### 4.2 Organizations Endpoints

#### GET /api/organizations
**Query Parameters:**
- `search`: String (optional)
- `page`: Integer (default: 1)
- `size`: Integer (default: 10)
- `plan`: String (optional)

#### POST /api/organizations
```json
{
    "name": "Kafe Do'stlar",
    "phone": "901234567",
    "boss": "Ali Valiyev",
    "plan": "Basic",
    "registrator_id": 1,
    "registration_date": "2024-06-15",
    "plan_expiration_days": 25
}
```

#### GET /api/organizations/{id}
#### PUT /api/organizations/{id}
#### DELETE /api/organizations/{id}

#### GET /api/organizations/{id}/branches
#### POST /api/organizations/{id}/branches
```json
{
    "name": "Asosiy Filial",
    "location": "Toshkent shahri, Chilonzor"
}
```

#### GET /api/organizations/{id}/devices
#### POST /api/organizations/{id}/devices
```json
{
    "branch_id": 1,
    "name": "Kassa 1",
    "os": "Windows 10 Pro"
}
```

#### PUT /api/organizations/{id}/devices/{device_id}
#### DELETE /api/organizations/{id}/devices/{device_id}

#### GET /api/organizations/{id}/add-ons
#### POST /api/organizations/{id}/add-ons
```json
{
    "type": "branch",
    "quantity": 1,
    "monthly_price": 50000
}
```

#### DELETE /api/organizations/{id}/add-ons/{addon_id}

### 4.3 Users Endpoints

#### GET /api/users
**Query Parameters:**
- `search`: String (optional)
- `page`: Integer (default: 1)
- `size`: Integer (default: 10)
- `role`: String (optional)

#### POST /api/users
```json
{
    "full_name": "John Doe",
    "phone": "901234567",
    "password": "password123",
    "address": "Tashkent, Uzbekistan",
    "role": "registrator",
    "share_percentage": 10.50
}
```

#### GET /api/users/{id}
#### PUT /api/users/{id}
#### DELETE /api/users/{id}

#### GET /api/users/balances
**Response:**
```json
{
    "users": [
        {
            "id": 1,
            "full_name": "John Doe",
            "share_percentage": 10.50,
            "total_earnings": 1500000,
            "total_payouts": 1200000,
            "current_balance": 300000
        }
    ]
}
```

### 4.4 Payments Endpoints

#### GET /api/payments
**Query Parameters:**
- `organization_id`: Integer (optional)
- `start_date`: Date (optional)
- `end_date`: Date (optional)
- `source`: String (optional)
- `page`: Integer (default: 1)
- `size`: Integer (default: 10)

#### POST /api/payments
```json
{
    "organization_id": 1,
    "amount": 150000,
    "source": "Subscription",
    "payment_date": "2024-06-15"
}
```

#### GET /api/payments/sverka/{organization_id}
**Query Parameters:**
- `start_date`: Date (required)
- `end_date`: Date (required)

### 4.5 User Payouts Endpoints

#### GET /api/user-payouts
**Query Parameters:**
- `user_id`: Integer (optional)
- `start_date`: Date (optional)
- `end_date`: Date (optional)
- `page`: Integer (default: 1)
- `size`: Integer (default: 10)

#### POST /api/user-payouts
```json
{
    "user_id": 1,
    "amount": 50000,
    "source": "O'tkazma",
    "payout_date": "2024-06-15"
}
```

#### DELETE /api/user-payouts/{id}

### 4.6 Plans Endpoints

#### GET /api/plans
#### POST /api/plans
```json
{
    "name": "Premium Plus",
    "branches": 200,
    "devices_per_branch": 150,
    "waiters": 200,
    "kds": true,
    "warehouse_control": "pro",
    "tech_card": "pro",
    "chat_support": true,
    "api_integrations": ["Uzum tezkor", "Yandex delivery"],
    "phone_support_247": true,
    "personal_manager": true,
    "monthly_price": 500000,
    "yearly_price": 5000000,
    "flag": "Premium",
    "color": "#6a1b9a"
}
```

#### GET /api/plans/{id}
#### PUT /api/plans/{id}
#### DELETE /api/plans/{id}

### 4.7 Registration Requests Endpoints

#### GET /api/registration-requests
#### POST /api/registration-requests/{id}/approve
```json
{
    "share_percentage": 15.50
}
```

#### POST /api/registration-requests/{id}/reject

## 5. Security Requirements

### 5.1 Authentication
- JWT token-based authentication
- Token expiration: 24 hours
- Refresh token mechanism
- Password hashing with bcrypt (salt rounds: 12)

### 5.2 Authorization
- Role-based access control (RBAC)
- Admin: Full access to all endpoints
- Moderator: Read access + limited write access
- Registrator: Limited access to assigned organizations

### 5.3 Input Validation
- Pydantic models for request/response validation
- SQL injection prevention with SQLAlchemy ORM
- XSS protection with proper content-type headers
- Rate limiting: 100 requests per minute per IP

### 5.4 CORS Configuration
```python
CORS_ORIGINS = [
    "http://localhost:3000",
    "http://localhost:5173",
    "https://your-frontend-domain.com"
]
```

## 6. Error Handling

### 6.1 Standard Error Response Format
```json
{
    "error": {
        "code": "VALIDATION_ERROR",
        "message": "Invalid input data",
        "details": {
            "field": "phone",
            "issue": "Phone number format is invalid"
        }
    }
}
```

### 6.2 HTTP Status Codes
- 200: Success
- 201: Created
- 400: Bad Request
- 401: Unauthorized
- 403: Forbidden
- 404: Not Found
- 422: Validation Error
- 500: Internal Server Error

## 7. Database Migrations

### 7.1 Alembic Configuration
- Database migration management with Alembic
- Version control for schema changes
- Rollback capabilities

### 7.2 Initial Migration
```bash
alembic init alembic
alembic revision --autogenerate -m "Initial migration"
alembic upgrade head
```

## 8. Environment Configuration

### 8.1 Environment Variables
```bash
# Database
DATABASE_URL=postgresql://user:password@localhost:5432/admin_panel

# Security
SECRET_KEY=your-secret-key-here
ALGORITHM=HS256
ACCESS_TOKEN_EXPIRE_MINUTES=1440

# CORS
CORS_ORIGINS=http://localhost:3000,http://localhost:5173

# Logging
LOG_LEVEL=INFO
```

### 8.2 Railway.com Configuration
- Automatic deployment from Git repository
- Environment variables management
- PostgreSQL database provisioning
- SSL certificate management

## 9. Local Development Setup

### 9.1 Docker Compose
```yaml
version: '3.8'
services:
  db:
    image: postgres:15
    environment:
      POSTGRES_DB: admin_panel
      POSTGRES_USER: admin
      POSTGRES_PASSWORD: password
    ports:
      - "5432:5432"
    volumes:
      - postgres_data:/var/lib/postgresql/data

  api:
    build: .
    ports:
      - "8000:8000"
    environment:
      DATABASE_URL: postgresql://admin:password@db:5432/admin_panel
      SECRET_KEY: dev-secret-key
    depends_on:
      - db

volumes:
  postgres_data:
```

### 9.2 Requirements.txt
```
fastapi==0.104.1
uvicorn[standard]==0.24.0
sqlalchemy==2.0.23
alembic==1.12.1
psycopg2-binary==2.9.9
pydantic==2.5.0
pydantic-settings==2.1.0
python-jose[cryptography]==3.3.0
passlib[bcrypt]==1.7.4
python-multipart==0.0.6
```

## 10. Default Data

### 10.1 Default Admin User
```sql
INSERT INTO users (full_name, phone, password_hash, role, share_percentage) 
VALUES (
    'Admin User', 
    'admin', 
    '$2b$12$LQv3c1yqBWVHxkd0LHAkCOYz6TtxMQJqhN8/LewdBPj4J/HS.iK2i', -- admin123
    'admin', 
    0.00
);
```

### 10.2 Default Plans
```sql
INSERT INTO custom_plans (name, branches, devices_per_branch, waiters, kds, warehouse_control, tech_card, chat_support, api_integrations, phone_support_247, personal_manager, monthly_price, yearly_price, flag, color) VALUES
('Free', 1, 2, 0, false, 'none', 'none', false, '{}', false, false, 0, 0, 'Hamyonbop', '#6c757d'),
('Basic', 5, 10, 5, true, 'lite', 'lite', true, '{"Uzum tezkor"}', false, false, 150000, 1500000, 'Ommabop', '#007bff'),
('Premium', 100, 100, 100, true, 'pro', 'pro', true, '{"Uzum tezkor", "Yandex delivery", "Wolt"}', true, true, 400000, 4000000, 'Premium', '#6a1b9a');
```

## 11. API Documentation

### 11.1 Swagger UI
- Available at `/docs`
- Interactive API documentation
- Request/response examples
- Authentication testing

### 11.2 ReDoc
- Available at `/redoc`
- Alternative documentation format
- Better for complex schemas

## 12. Monitoring and Logging

### 12.1 Logging Configuration
- Structured logging with JSON format
- Log levels: DEBUG, INFO, WARNING, ERROR
- Request/response logging
- Database query logging (development only)

### 12.2 Health Check Endpoint
```
GET /health
Response: {"status": "healthy", "timestamp": "2024-06-15T10:30:00Z"}
```

## 13. Testing Strategy

### 13.1 Unit Tests
- Pydantic model validation tests
- Service layer business logic tests
- Repository layer data access tests

### 13.2 Integration Tests
- API endpoint tests
- Database integration tests
- Authentication flow tests

### 13.3 Test Dependencies
```
pytest==7.4.3
pytest-asyncio==0.21.1
httpx==0.25.2
factory-boy==3.3.0
```

## 14. Deployment Checklist

### 14.1 Pre-deployment
- [ ] All tests passing
- [ ] Environment variables configured
- [ ] Database migrations ready
- [ ] Security audit completed
- [ ] API documentation updated

### 14.2 Railway.com Deployment
- [ ] Connect Git repository
- [ ] Configure environment variables
- [ ] Set up PostgreSQL database
- [ ] Configure custom domain (optional)
- [ ] Enable automatic deployments

### 14.3 Post-deployment
- [ ] Verify health check endpoint
- [ ] Test authentication flow
- [ ] Verify database connections
- [ ] Monitor error logs
- [ ] Performance testing

## 15. Performance Requirements

### 15.1 Response Times
- API endpoints: < 500ms (95th percentile)
- Database queries: < 100ms
- Authentication: < 200ms

### 15.2 Scalability
- Support for 1000+ concurrent users
- Database connection pooling
- Caching for frequently accessed data
- Pagination for large datasets

## 16. Backup and Recovery

### 16.1 Database Backups
- Daily automated backups
- Point-in-time recovery capability
- Backup retention: 30 days

### 16.2 Disaster Recovery
- Multi-region deployment capability
- Automated failover procedures
- Data recovery procedures documented

## 17. Maintenance and Updates

### 17.1 Regular Maintenance
- Weekly security updates
- Monthly dependency updates
- Quarterly performance reviews

### 17.2 Monitoring
- Application performance monitoring
- Database performance monitoring
- Error rate monitoring
- Uptime monitoring

---

**Loyiha Yaratuvchisi:** AI Assistant  
**Yaratilgan Sana:** 2024-yil  
**Versiya:** 1.0  
**Status:** Tayyor