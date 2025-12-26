from sqlalchemy.orm import Session

from app.core.database import SessionLocal
from app.core.security import get_password_hash
from app.core.config import settings
from app.models.user import User
from app.models.package import Package


def init_db() -> None:
    """
    Initialize database with default data
    - Create first superuser if not exists
    - Create default packages if not exists
    """
    db = SessionLocal()
    
    try:
        # Create first superuser
        user = db.query(User).filter(User.email == settings.FIRST_SUPERUSER_EMAIL).first()
        
        if not user:
            user = User(
                email=settings.FIRST_SUPERUSER_EMAIL,
                username="admin",
                full_name=settings.FIRST_SUPERUSER_NAME,
                hashed_password=get_password_hash(settings.FIRST_SUPERUSER_PASSWORD),
                is_superuser=True,
                is_active=True,
                role="admin"
            )
            db.add(user)
            db.commit()
            print(f"✅ Created superuser: {settings.FIRST_SUPERUSER_EMAIL}")
        else:
            print(f"ℹ️  Superuser already exists: {settings.FIRST_SUPERUSER_EMAIL}")
        
        # Create default packages if not exists
        package_count = db.query(Package).count()
        
        if package_count == 0:
            default_packages = [
                {
                    "name": "Paket Basic 10 Mbps",
                    "code": "PKG-10M",
                    "description": "Paket internet rumah basic untuk browsing dan streaming",
                    "download_speed": 10,
                    "upload_speed": 5,
                    "price": 200000,
                    "installation_fee": 300000,
                    "quota_gb": 0,
                    "package_type": "residential",
                    "is_active": True,
                    "is_featured": False,
                    "sort_order": 1
                },
                {
                    "name": "Paket Standard 20 Mbps",
                    "code": "PKG-20M",
                    "description": "Paket internet rumah untuk keluarga",
                    "download_speed": 20,
                    "upload_speed": 10,
                    "price": 350000,
                    "installation_fee": 300000,
                    "quota_gb": 0,
                    "package_type": "residential",
                    "is_active": True,
                    "is_featured": True,
                    "sort_order": 2
                },
                {
                    "name": "Paket Premium 50 Mbps",
                    "code": "PKG-50M",
                    "description": "Paket internet premium untuk streaming 4K dan gaming",
                    "download_speed": 50,
                    "upload_speed": 25,
                    "price": 550000,
                    "installation_fee": 300000,
                    "quota_gb": 0,
                    "package_type": "residential",
                    "is_active": True,
                    "is_featured": True,
                    "sort_order": 3
                },
                {
                    "name": "Paket Business 100 Mbps",
                    "code": "PKG-100M",
                    "description": "Paket internet untuk bisnis dan kantor",
                    "download_speed": 100,
                    "upload_speed": 50,
                    "price": 1200000,
                    "installation_fee": 500000,
                    "quota_gb": 0,
                    "package_type": "business",
                    "is_active": True,
                    "is_featured": False,
                    "sort_order": 4
                }
            ]
            
            for pkg_data in default_packages:
                package = Package(**pkg_data)
                db.add(package)
            
            db.commit()
            print(f"✅ Created {len(default_packages)} default packages")
        else:
            print(f"ℹ️  Packages already exist: {package_count} packages")
            
    except Exception as e:
        print(f"❌ Error initializing database: {e}")
        db.rollback()
    finally:
        db.close()
