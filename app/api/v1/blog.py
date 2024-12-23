from fastapi import APIRouter, Depends, HTTPException, UploadFile, File, Form, status
from sqlalchemy.orm import Session,Query
from typing import List, Optional
from datetime import datetime
from fastapi.security import OAuth2PasswordBearer
import os
import uuid
import aiofiles


from app.db.database import get_db
from app.models.blog import Blog
from app.models.user import CustomUser
from app.schema.blog import BlogCreate, BlogResponse, BlogUpdate,PaginatedBlogResponse
from app.utils.headers_accessing import validate_and_send_user
from sqlalchemy import desc
from math import ceil


router = APIRouter()


async def save_blog_picture(image: UploadFile) -> str:
    """
    Asynchronously saves an uploaded blog image and returns the file path.
    """
    # Create upload directory if it doesn't exist
    UPLOAD_DIR = "uploads/blog_images"
    os.makedirs(UPLOAD_DIR, exist_ok=True)
    
    # Generate unique filename
    file_extension = os.path.splitext(image.filename)[1]
    unique_filename = f"{uuid.uuid4()}{file_extension}"
    
    # Create year/month based directory structure
    current_date = datetime.now()
    year_month_dir = os.path.join(UPLOAD_DIR, f"{current_date.year}/{current_date.month:02d}")
    os.makedirs(year_month_dir, exist_ok=True)
    
    # Complete file path
    file_path = os.path.join(year_month_dir, unique_filename)
    
    try:
        # Asynchronously write the file
        async with aiofiles.open(file_path, 'wb') as out_file:
            content = await image.read()
            await out_file.write(content)
            
        # Return the relative path to be stored in database
        return file_path
    except Exception as e:
        # If there's an error, ensure we don't leave a partially written file
        if os.path.exists(file_path):
            os.remove(file_path)
        raise Exception(f"Failed to save image: {str(e)}")


@router.get("/blogs/", response_model=PaginatedBlogResponse)
async def get_all_blogs(
    page: int = 1,
    page_size: int = 6,
    search: Optional[str] = None,
    db: Session = Depends(get_db)
):
    try:
        # Calculate offset
        offset = (page - 1) * page_size

        # Base query
        query = db.query(Blog)

        # Add search functionality if search parameter is provided
        if search:
            search_term = f"%{search}%"
            query = query.filter(
                (Blog.title.ilike(search_term)) |
                (Blog.short_description.ilike(search_term))
            )

        # Get total count
        total_blogs = query.count()

        # Calculate total pages
        total_pages = ceil(total_blogs / page_size)

        # Get paginated results
        blogs = query.order_by(desc(Blog.created_at))\
                    .offset(offset)\
                    .limit(page_size)\
                    .all()

        # Calculate pagination metadata
        has_next = page < total_pages
        has_previous = page > 1

        return {
            "results": blogs,
            "total_pages": total_pages,
            "current_page": page,
            "total_blogs": total_blogs,
            "has_next": has_next,
            "has_previous": has_previous
        }

    except Exception as e:
        raise HTTPException(
            status_code=500,
            detail=f"Error fetching blogs: {str(e)}"
        )
    

# Create a new blog post
@router.post("/blogs/", response_model=BlogResponse, status_code=status.HTTP_201_CREATED)
async def create_blog(
    title: str = Form(...),
    short_description: str = Form(...),
    content: str = Form(...),
    image: Optional[UploadFile] = File(None),
    current_user: CustomUser = Depends(validate_and_send_user),
    db: Session = Depends(get_db)
):
    try:
        # Handle image upload
        image_path = None
        if image:
            image_path = await save_blog_picture(image)

        new_blog = Blog(
            title=title,
            short_description=short_description,
            content=content,
            image=image_path,
            author_id=current_user.id
        )
        
        db.add(new_blog)
        db.commit()
        db.refresh(new_blog)
        
        return new_blog
    except Exception as e:
        db.rollback()
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Error creating blog post: {str(e)}"
        )

# Get user's blogs
@router.get("/get-my-blogs/", response_model=List[BlogResponse])
async def get_my_blogs(
    current_user: CustomUser = Depends(validate_and_send_user),
    db: Session = Depends(get_db),
    skip: int = 0,
    limit: int = 10
):
    blogs = db.query(Blog)\
        .filter(Blog.author_id == current_user.id)\
        .order_by(Blog.created_at.desc())\
        .offset(skip)\
        .limit(limit)\
        .all()
    
    return blogs

# Get specific blog by ID
@router.get("/get-blog/{blog_id}", response_model=BlogResponse)
async def get_blog(
    blog_id: int,
    current_user: CustomUser = Depends(validate_and_send_user),
    db: Session = Depends(get_db)
):
    blog = db.query(Blog)\
        .filter(Blog.id == blog_id, Blog.author_id == current_user.id)\
        .first()
    
    if not blog:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Blog post not found"
        )
    
    return blog

# Update blog
@router.put("/update-blog/{blog_id}/", response_model=BlogResponse)
async def update_blog(
    blog_id: int,
    title: str = Form(...),
    short_description: str = Form(...),
    content: str = Form(...),
    image: Optional[UploadFile] = File(None),
    current_user: CustomUser = Depends(validate_and_send_user),
    db: Session = Depends(get_db)
):
    blog = db.query(Blog)\
        .filter(Blog.id == blog_id, Blog.author_id == current_user.id)\
        .first()
    
    if not blog:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Blog post not found"
        )

    try:
        # Handle image upload if new image is provided
        if image:
            # Delete old image if exists
            if blog.image and os.path.exists(blog.image):
                os.remove(blog.image)
            image_path = await save_blog_picture(image)
            blog.image = image_path

        blog.title = title
        blog.short_description = short_description
        blog.content = content
        
        db.commit()
        db.refresh(blog)
        
        return blog
    except Exception as e:
        db.rollback()
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Error updating blog post: {str(e)}"
        )

# Delete blog
@router.delete("/my-blogs/{blog_id}/", status_code=status.HTTP_204_NO_CONTENT)
async def delete_blog(
    blog_id: int,
    current_user: CustomUser = Depends(validate_and_send_user),
    db: Session = Depends(get_db)
):
    blog = db.query(Blog)\
        .filter(Blog.id == blog_id, Blog.author_id == current_user.id)\
        .first()
    
    if not blog:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Blog post not found"
        )

    try:
        # Delete associated image if exists
        if blog.image and os.path.exists(blog.image):
            os.remove(blog.image)
            
        db.delete(blog)
        db.commit()
    except Exception as e:
        db.rollback()
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Error deleting blog post: {str(e)}"
        )