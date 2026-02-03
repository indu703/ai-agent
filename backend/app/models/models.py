from datetime import datetime
from app.core.config import settings
from sqlalchemy import Integer, String, Boolean, DateTime, ForeignKey, PickleType
from sqlalchemy.orm import relationship, Mapped, mapped_column
from sqlalchemy.sql import func
try:
    from pgvector.sqlalchemy import Vector
    # We still check LITE_MODE because the extension might be missing on the server
    HAS_PGVECTOR = not settings.LITE_MODE
except ImportError:
    HAS_PGVECTOR = False
from app.db.session import Base

class Staff(Base):
    __tablename__ = "staff"
    
    id: Mapped[int] = mapped_column(Integer, primary_key=True, index=True)
    staff_id: Mapped[str] = mapped_column(String, unique=True, index=True) # e.g. EMP_1021
    name: Mapped[str] = mapped_column(String)
    role: Mapped[str] = mapped_column(String)
    status: Mapped[str] = mapped_column(String, default="active") # active, inactive
    created_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), server_default=func.now())
    
    embeddings: Mapped[list["FaceEmbedding"]] = relationship(back_populates="staff", cascade="all, delete-orphan")

class FaceEmbedding(Base):
    __tablename__ = "face_embeddings"
    
    id: Mapped[int] = mapped_column(Integer, primary_key=True, index=True)
    staff_id: Mapped[int] = mapped_column(Integer, ForeignKey("staff.id"))
    # Use Vector type if pgvector is available, otherwise fallback to PickleType (standard serialization)
    if HAS_PGVECTOR:
        embedding = mapped_column(Vector(512)) # ArcFace default is 512
    else:
        embedding = mapped_column(PickleType)
    active: Mapped[bool] = mapped_column(Boolean, default=True)
    
    staff: Mapped["Staff"] = relationship(back_populates="embeddings")

class Admin(Base):
    __tablename__ = "admins"
    
    id: Mapped[int] = mapped_column(Integer, primary_key=True, index=True)
    username: Mapped[str] = mapped_column(String, unique=True, index=True)
    password_hash: Mapped[str] = mapped_column(String)
