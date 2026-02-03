from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from contextlib import asynccontextmanager
from app.core.config import settings
from app.db.session import engine, Base, SessionLocal
from app.models.models import Admin
from app.core.security import get_password_hash
from sqlalchemy import text
from app.api.endpoints import auth, staff, recognition

@asynccontextmanager
async def lifespan(app: FastAPI):
    # Startup logic
    print("Creating tables...")
    try:
        # Create tables (including vector extension if handled by alchemy, but usually needs raw sql for extension)
        # We need to ensure 'vector' extension exists.
        with engine.connect() as conn:
            try:
                conn.execute(text("CREATE EXTENSION IF NOT EXISTS vector"))
                conn.commit()
            except Exception as e:
                print(f"Warning: pgvector extension not available. Face search will use fallback logic. Error: {e}")
        
        Base.metadata.create_all(bind=engine)
        
        # Seed Admin
        db = SessionLocal()
        admin = db.query(Admin).filter(Admin.username == "admin").first()
        if not admin:
            print("Seeding default admin...")
            admin = Admin(
                username="admin",
                password_hash=get_password_hash("Admin@123")
            )
            db.add(admin)
            db.commit()
            print("Seeding default admin: SUCCESS")
        else:
            print("Syncing admin password...")
            admin.password_hash = get_password_hash("Admin@123")
            db.commit()
            print("Admin password sync: SUCCESS")
        db.close()
    except Exception as e:
        print(f"FATAL ERROR during startup/seeding: {e}")
        print("CRITICAL: Admin user was NOT created/updated.")
    
    yield
    # Shutdown logic

app = FastAPI(title=settings.PROJECT_NAME, lifespan=lifespan)

# CORS
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Routers
app.include_router(auth.router, prefix="/api/auth", tags=["auth"])
app.include_router(staff.router, prefix="/api/staff", tags=["staff"])
app.include_router(recognition.router, prefix="/api/recognition", tags=["recognition"])

@app.get("/")
def root():
    return {"message": "Face Recognition API is running"}

# Need to import text for raw sql (already moved to top)
