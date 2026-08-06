# SKProducts - Enterprise Order Management System

A production-ready, enterprise-level Order Management System built with FastAPI and React, following industry best practices and modern software architecture patterns.

## 🚀 Features

### Core Functionality
- **User Management**: Create, edit, delete users with role-based access
- **Order Management**: Create, edit, track orders with status lifecycle
- **Role-Based Access Control (RBAC)**: ADMIN, IDENTITY, and Normal User roles
- **Identity Profiles**: Unique identity IDs for IDENTITY role users
- **Stock Management**: Track product availability (IN_STOCK/OUT_OF_STOCK)
- **Profile Management**: Users can edit their profile and change password

### Security Features
- JWT authentication with short-lived access tokens (30 minutes)
- Refresh token mechanism for seamless authentication
- Rate limiting on login endpoint (5 attempts/minute)
- Password hashing with bcrypt
- Input validation and SQL injection prevention
- CORS configuration
- Request ID tracking for debugging

### Technical Features
- **Backend**: FastAPI, SQLAlchemy ORM, Alembic migrations
- **Frontend**: React, Material UI, React Query, Axios
- **Database**: SQLite (dev), PostgreSQL/MySQL (production ready)
- **Architecture**: Repository Pattern, Service Layer, Dependency Injection
- **Logging**: Request/response logging with timing
- **Error Handling**: Consistent error format with request IDs

---

## 📁 Project Structure

```
SKProducts/
├── backend/
│   ├── app/
│   │   ├── api/
│   │   │   └── v1/                    # API routes
│   │   │       ├── auth.py
│   │   │       ├── users.py
│   │   │       ├── orders.py
│   │   │       ├── user_orders.py
│   │   │       └── profile.py
│   │   ├── core/
│   │   │   ├── config.py             # Settings management
│   │   │   ├── security.py           # JWT, password hashing
│   │   │   └── logging.py
│   │   ├── database/
│   │   │   └── database.py           # SQLAlchemy setup
│   │   ├── models/                   # SQLAlchemy models
│   │   │   ├── user.py
│   │   │   ├── role.py
│   │   │   ├── user_role.py
│   │   │   ├── order.py
│   │   │   ├── user_order.py
│   │   │   ├── identity_profile.py
│   │   │   └── token.py
│   │   ├── schemas/                  # Pydantic schemas
│   │   ├── repositories/             # Data access layer
│   │   ├── services/                 # Business logic
│   │   ├── dependencies/             # FastAPI dependencies
│   │   ├── middleware/               # Custom middleware
│   │   ├── exceptions/               # Error handlers
│   │   ├── utils/                    # Utilities
│   │   └── main.py                   # App entry point
│   ├── migrations/                   # Alembic migrations
│   ├── tests/                        # Test suite
│   ├── uploads/                      # File uploads
│   ├── requirements.txt
│   └── .env.example
├── frontend/
│   ├── src/
│   │   ├── api/                      # API clients
│   │   ├── hooks/                    # React Query hooks
│   │   ├── contexts/                 # React contexts
│   │   ├── layouts/                  # Layout components
│   │   ├── pages/                    # Page components
│   │   ├── routes/                   # Route protection
│   │   ├── theme/                    # MUI theme
│   │   ├── App.jsx
│   │   └── main.jsx
│   ├── package.json
│   ├── vite.config.js
│   └── index.html
├── docker-compose.yml
├── Dockerfile.backend
├── Dockerfile.frontend
└── README.md
```

---

## 🛠️ Technology Stack

### Backend
- **Framework**: FastAPI 0.111.0
- **Language**: Python 3.10+
- **ORM**: SQLAlchemy 2.0.31
- **Migrations**: Alembic 1.13.2
- **Authentication**: JWT (python-jose), bcrypt (passlib)
- **Validation**: Pydantic 2.8.2
- **Server**: Uvicorn

### Frontend
- **Framework**: React 19.2.8
- **Build Tool**: Vite 8.1.5
- **UI Library**: Material UI 9.2.0
- **State Management**: React Query 5.17.0
- **Routing**: React Router 7.18.1
- **HTTP Client**: Axios 1.18.1
- **Notifications**: Notistack 3.0.2

---

## 📋 Prerequisites

- Python 3.10 or higher
- Node.js 18+ and npm
- PostgreSQL (optional, for production)
- Git

---

## 🔧 Installation

### Backend Setup

1. **Clone the repository**
```bash
git clone <repository-url>
cd SKProducts/backend
```

2. **Create virtual environment**
```bash
python -m venv venv

# Windows
venv\Scripts\activate

# Linux/Mac
source venv/bin/activate
```

3. **Install dependencies**
```bash
pip install -r requirements.txt
```

4. **Configure environment**
```bash
# Copy example env file
cp .env.example .env

# Edit .env with your settings
# IMPORTANT: Generate a secure SECRET_KEY!
python -c "import secrets; print(secrets.token_hex(32))"
```

5. **Run database migrations**
```bash
alembic upgrade head
```

6. **Start the backend server**
```bash
# Development
uvicorn main:app --reload

# Production
gunicorn main:app -w 4 -k uvicorn.workers.UvicornWorker --bind 0.0.0.0:8000
```

The API will be available at `http://localhost:8000`
- API Documentation: `http://localhost:8000/docs`
- Alternative docs: `http://localhost:8000/redoc`

### Frontend Setup

1. **Install dependencies**
```bash
cd ../frontend
npm install
```

2. **Start development server**
```bash
npm run dev
```

The frontend will be available at `http://localhost:5173`

3. **Build for production**
```bash
npm run build
```

---

## 🔐 Default Credentials

**Admin Account:**
- Email: `admin@skcompany.com`
- Password: `admin@12345`

⚠️ **Change these credentials in production!**

---

## 👥 User Roles

### Normal User (Default)
- View all available orders
- Select orders
- View own orders
- Cancel own orders (before processing)
- Edit own profile
- Change password

### IDENTITY Role
- All Normal User permissions
- View all users
- Edit user profiles
- Reset user passwords
- Cannot assign ADMIN role

### ADMIN Role
- All permissions
- Create/edit/delete users
- Manage roles
- Create/edit/delete orders
- Change order status
- Assign any role

---

## 🗄️ Database Schema

### Tables
- **users**: User accounts
- **roles**: Available roles (IDENTITY, ADMIN)
- **user_roles**: Many-to-many user-role relationships
- **orders**: Order/product catalog
- **user_orders**: User order selections with status
- **identity_profiles**: Identity-specific profiles
- **refresh_tokens**: Refresh token storage

### Migrations
```bash
# Create new migration
alembic revision --autogenerate -m "description"

# Apply migrations
alembic upgrade head

# Rollback one migration
alembic downgrade -1
```

---

## 🧪 Testing

### Run Backend Tests
```bash
cd backend
pytest tests/ -v
```

### Test Coverage
```bash
pytest tests/ --cov=app --cov-report=html
```

---

## 🚢 Deployment

### Using Docker (Recommended)

```bash
# Build and start all services
docker-compose up -d

# View logs
docker-compose logs -f

# Stop services
docker-compose down
```

### Manual Deployment

#### Backend
```bash
cd backend
python -m venv venv
source venv/bin/activate
pip install -r requirements.txt

# Set environment variables
export SECRET_KEY=<your-secret-key>
export ENVIRONMENT=production
export DATABASE_URL=postgresql://user:pass@localhost/skproducts

# Run migrations
alembic upgrade head

# Start with Gunicorn
gunicorn main:app -w 4 -k uvicorn.workers.UvicornWorker --bind 0.0.0.0:8000
```

#### Frontend
```bash
cd frontend
npm install
npm run build

# Serve with Nginx
# Copy dist/ folder to your web server
```

#### Nginx Configuration
```nginx
server {
    listen 80;
    server_name yourdomain.com;

    # Frontend
    location / {
        root /var/www/skproducts/frontend/dist;
        try_files $uri $uri/ /index.html;
    }

    # Backend API
    location /api/ {
        proxy_pass http://127.0.0.1:8000;
        proxy_set_header Host $host;
        proxy_set_header X-Real-IP $remote_addr;
        proxy_set_header X-Forwarded-For $proxy_add_x_forwarded_for;
    }

    # Uploads
    location /uploads/ {
        proxy_pass http://127.0.0.1:8000/uploads/;
    }
}
```

---

## 🔒 Security Considerations

### Production Checklist
- [ ] Set strong `SECRET_KEY` in `.env`
- [ ] Use PostgreSQL instead of SQLite
- [ ] Enable HTTPS with SSL certificates
- [ ] Configure CORS origins properly
- [ ] Set `ENVIRONMENT=production`
- [ ] Disable `DEBUG` mode
- [ ] Use environment variables for all secrets
- [ ] Regular security updates
- [ ] Database backups
- [ ] Rate limiting enabled
- [ ] File upload validation
- [ ] Account lockout enabled

### Environment Variables
```env
# Required in production
SECRET_KEY=<64-char-hex-key>
ENVIRONMENT=production
DATABASE_URL=postgresql://user:pass@localhost/skproducts

# Optional
CORS_ORIGINS=https://yourdomain.com,https://admin.yourdomain.com
LOG_LEVEL=INFO
ACCESS_TOKEN_EXPIRE_MINUTES=30
REFRESH_TOKEN_EXPIRE_DAYS=7
```

---

## 📊 API Endpoints

### Authentication
- `POST /api/v1/auth/login` - Login
- `GET /api/v1/auth/me` - Get current user
- `POST /api/v1/auth/refresh` - Refresh access token

### Users
- `GET /api/v1/users` - List users (Admin/Identity)
- `POST /api/v1/users` - Create user (Admin/Identity)
- `GET /api/v1/users/{id}` - Get user (Admin/Identity)
- `PUT /api/v1/users/{id}` - Update user (Admin/Identity)
- `DELETE /api/v1/users/{id}` - Delete user (Admin only)
- `PUT /api/v1/users/{id}/roles` - Update user roles (Admin only)
- `PUT /api/v1/users/{id}/reset-password` - Reset password (Admin/Identity)

### Orders
- `GET /api/v1/orders` - List all orders
- `POST /api/v1/orders` - Create order (Admin only)
- `GET /api/v1/orders/{id}` - Get order details
- `PUT /api/v1/orders/{id}` - Update order (Admin only)
- `DELETE /api/v1/orders/{id}` - Delete order (Admin only)
- `PATCH /api/v1/orders/{id}/stock` - Update stock status (Admin only)

### User Orders
- `POST /api/v1/orders/{id}/select` - Select an order
- `GET /api/v1/my-orders` - Get my orders
- `PATCH /api/v1/my-orders/{id}/cancel` - Cancel my order
- `PATCH /api/v1/my-orders/{id}/status` - Update order status (Admin only)

### Profile
- `GET /api/v1/profile` - Get my profile
- `PUT /api/v1/profile` - Update my profile
- `PUT /api/v1/profile/password` - Change password

---

## 🐛 Troubleshooting

### Backend won't start
- Check if port 8000 is already in use
- Verify `.env` file exists and has required variables
- Check database connection

### Frontend build fails
- Delete `node_modules` and run `npm install` again
- Clear Vite cache: `npm run dev -- --force`

### Database errors
- Run `alembic upgrade head` to apply migrations
- Check database URL in `.env`
- Ensure database user has proper permissions

### Tests fail
- Ensure test database is clean
- Check that seed data is created
- Verify all dependencies are installed

---

## 📝 License

This project is proprietary software. All rights reserved.

---

## 👨‍💻 Development

### Code Standards
- Follow PEP 8 for Python code
- Use type hints everywhere
- Write tests for new features
- Update documentation

### Contributing
1. Create a feature branch
2. Make your changes
3. Run tests: `pytest tests/ -v`
4. Submit a pull request

---

## 📞 Support

For issues and questions, please contact the development team.

---

## 🎯 Roadmap

- [x] Core authentication and authorization
- [x] User and order management
- [x] Role-based access control
- [x] Production-grade security
- [x] Database migrations
- [x] Frontend with React Query
- [ ] Email notifications
- [ ] Advanced analytics dashboard
- [ ] Bulk order operations
- [ ] Export to CSV/PDF
- [ ] Mobile app (React Native)
- [ ] Multi-language support
- [ ] Audit logging
- [ ] Advanced reporting

---

**Built with ❤️ by the SKProducts Team**