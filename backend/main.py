"""SKProducts Order Management System - Main Application Entry Point."""

import os
import uuid
import logging
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from fastapi.staticfiles import StaticFiles
from app.core.config import settings
from app.database.database import engine, Base, SessionLocal
from app.core.security import get_password_hash
from app.models.user import User
from app.models.role import Role
from app.models.user_role import UserRole
from app.exceptions.handlers import register_exception_handlers
from app.middleware.logging_middleware import RequestLoggingMiddleware
from app.middleware.rate_limit import RateLimitMiddleware
from app.middleware.security_headers import SecurityHeadersMiddleware

# Configure logging
logging.basicConfig(
    level=getattr(logging, settings.LOG_LEVEL.upper(), logging.INFO),
    format=settings.LOG_FORMAT,
)
logger = logging.getLogger(__name__)


def seed_database():
    """Seed the database with initial data."""
    db = SessionLocal()
    try:
        # Create roles if they don't exist
        roles_existing = {r.name for r in db.query(Role).all()}

        roles_to_create = []
        for role_name in ["IDENTITY", "ADMIN"]:
            if role_name not in roles_existing:
                role = Role(id=str(uuid.uuid4()), name=role_name)
                db.add(role)
                roles_to_create.append(role_name)
                logger.info(f"Created role: {role_name}")

        if roles_to_create:
            db.commit()

        # Create default admin if not exists
        existing_admin = db.query(User).filter(User.email == settings.ADMIN_EMAIL).first()
        if not existing_admin:
            admin_id = str(uuid.uuid4())
            admin = User(
                id=admin_id,
                uuid=str(uuid.uuid4()),
                name=settings.ADMIN_NAME,
                email=settings.ADMIN_EMAIL,
                password_hash=get_password_hash(settings.ADMIN_PASSWORD),
                active=True
            )
            db.add(admin)
            db.commit()

            # Assign ADMIN role
            admin_role = db.query(Role).filter(Role.name == "ADMIN").first()
            if admin_role:
                user_role = UserRole(
                    id=str(uuid.uuid4()),
                    user_id=admin_id,
                    role_id=admin_role.id
                )
                db.add(user_role)
                db.commit()

            logger.info(f"Created default admin: {settings.ADMIN_EMAIL}")
        else:
            logger.info("Default admin already exists")

    except Exception as e:
        logger.error(f"Error seeding database: {e}")
        db.rollback()
    finally:
        db.close()


def create_application() -> FastAPI:
    """Create and configure the FastAPI application."""
    app = FastAPI(
        title=settings.APP_NAME,
        description="Enterprise Order Management System",
        version="1.0.0",
        docs_url="/docs",
        redoc_url="/redoc",
    )

    # Register exception handlers (must be before middleware)
    register_exception_handlers(app)

    # Add request logging middleware
    app.add_middleware(RequestLoggingMiddleware)

    # Add rate limiting middleware
    app.add_middleware(RateLimitMiddleware)

    # Add security headers middleware
    app.add_middleware(SecurityHeadersMiddleware)

    # CORS middleware
    app.add_middleware(
        CORSMiddleware,
        allow_origins=settings.cors_origins_list,
        allow_credentials=True,
        allow_methods=["*"],
        allow_headers=["*"],
    )

    # Create uploads directory
    os.makedirs(settings.UPLOAD_DIR, exist_ok=True)

    # Mount static files for uploads
    app.mount(f"/{settings.UPLOAD_DIR}", StaticFiles(directory=settings.UPLOAD_DIR), name=settings.UPLOAD_DIR)

    # Import and register routers
    from app.api.v1.auth import router as auth_router
    from app.api.v1.users import router as users_router
    from app.api.v1.orders import router as orders_router
    from app.api.v1.user_orders import router as user_orders_router
    from app.api.v1.profile import router as profile_router

    app.include_router(auth_router, prefix="/api/v1")
    app.include_router(users_router, prefix="/api/v1")
    app.include_router(orders_router, prefix="/api/v1")
    app.include_router(user_orders_router, prefix="/api/v1")
    app.include_router(profile_router, prefix="/api/v1")

    @app.get("/api/health")
    def health_check():
        return {"status": "healthy", "app": settings.APP_NAME}

    return app


app = create_application()


@app.on_event("startup")
def startup_event():
    """Run startup tasks."""
    logger.info(f"Starting {settings.APP_NAME}...")

    # Create all tables
    Base.metadata.create_all(bind=engine)
    logger.info("Database tables created")

    # Seed initial data
    seed_database()

    logger.info("Application startup complete")


if __name__ == "__main__":
    import uvicorn
    uvicorn.run(
        "main:app",
        host="0.0.0.0",
        port=8000,
        reload=True,
        log_level="info"
    )