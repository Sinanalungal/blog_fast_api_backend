from sqlalchemy import Column, Integer, String, Boolean
from sqlalchemy.orm import relationship
from app.db.database import Base

class CustomUser(Base):
    __tablename__ = "custom_user"

    id = Column(Integer, primary_key=True, index=True)
    username = Column(String, unique=True,nullable=False)
    email = Column(String, unique=True, nullable=False)
    is_active = Column(Boolean, default=True)
    role = Column(String, nullable=False, default='user')
    profile_picture = Column(String, nullable=True) 
    hashed_password = Column(String, nullable=False) 
    
    blogs = relationship("Blog", back_populates="author")
