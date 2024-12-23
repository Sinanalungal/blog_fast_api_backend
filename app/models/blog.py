from sqlalchemy import Column, Integer, String, Text, ForeignKey, DateTime
from sqlalchemy.orm import relationship
from datetime import datetime,timezone
from app.db.database import Base


class Blog(Base):
    __tablename__ = "blog"

    id = Column(Integer, primary_key=True, index=True)
    title = Column(String, nullable=False)
    short_description = Column(Text)
    content = Column(Text)
    image = Column(String, nullable=True)  
    author_id = Column(Integer, ForeignKey("custom_user.id"))
    created_at = Column(DateTime, default=datetime.now(timezone.utc))

    author = relationship("CustomUser", back_populates="blogs")
