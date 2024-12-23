from pydantic import BaseModel
from datetime import datetime
from typing import Optional,List

class BlogBase(BaseModel):
    title: str
    short_description: str
    content: str
    image: Optional[str] = None

class BlogCreate(BlogBase):
    pass

class BlogUpdate(BlogBase):
    pass

class BlogResponse(BlogBase):
    id: int
    author_id: int
    created_at: datetime

    class Config:
        from_attributes = True

class PaginatedBlogResponse(BaseModel):
    results: List[BlogResponse]
    total_pages: int
    current_page: int
    total_blogs: int
    has_next: bool
    has_previous: bool
