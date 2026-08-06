"""Test that all backend imports work correctly."""

import sys
import os
sys.path.insert(0, os.path.dirname(__file__))

# Test core imports
from app.core.config import settings
print(f"✓ Config loaded: {settings.APP_NAME}")

from app.core.security import verify_password, get_password_hash, create_access_token, decode_access_token
print("✓ Security imports OK")

# Test database
from app.database.database import Base, get_db
print("✓ Database imports OK")

# Test models
from app.models.user import User
from app.models.role import Role
from app.models.user_role import UserRole
from app.models.order import Order
from app.models.user_order import UserOrder
from app.models.identity_profile import IdentityProfile
print("✓ Model imports OK")

# Test schemas
from app.schemas.user import UserCreate, UserUpdate, UserResponse, PasswordChange, PasswordReset
from app.schemas.auth import LoginRequest, TokenResponse, RoleAssignment
from app.schemas.order import OrderCreate, OrderUpdate, OrderResponse, OrderStatusUpdate
print("✓ Schema imports OK")

# Test repositories
from app.repositories.user_repository import UserRepository
from app.repositories.order_repository import OrderRepository
print("✓ Repository imports OK")

# Test services
from app.services.auth_service import AuthService
from app.services.user_service import UserService
from app.services.order_service import OrderService
print("✓ Service imports OK")

# Test dependencies
from app.dependencies.auth_dependencies import get_current_user, has_roles, require_admin, require_identity, require_admin_or_identity
print("✓ Dependency imports OK")

# Test utils
from app.utils.file_upload import save_upload_file
print("✓ Utils imports OK")

# Test main app
from main import app
print("✓ Main app imports OK")

print("\n✅ All backend imports successful!")