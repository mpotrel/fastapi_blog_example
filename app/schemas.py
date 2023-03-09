from typing import Optional
from pydantic import BaseModel, EmailStr, ValidationError, validator
from datetime import datetime


class UserCreate(BaseModel):
    email: EmailStr
    password: str


class UserResponse(BaseModel):
    id: int
    email: EmailStr
    created_at: datetime

    class Config:
        orm_mode = True


class UserLogin(BaseModel):
    email: EmailStr
    password: str


class PostBase(BaseModel):
    title: str
    content: str
    published: bool = True


# The reason we use different classes is maybe we don't want to allow the user to update all values
class PostCreate(PostBase):
    pass


class Post(PostBase):
    id: int
    user_id: int
    created_at: datetime
    owner: UserResponse

    class Config:
        orm_mode = True


class PostWithVotes(PostBase):
    id: int
    user_id: int
    created_at: datetime
    votes: int

    class Config:
        orm_mode = True


class Vote(BaseModel):
    post_id: int
    dir: int

    @validator("dir")
    def dir_must_be_0_or_1(cls, v):
        if v in {0, 1}:
            return v
        raise ValidationError(f"dir is supposed to be 0 or 1, got {v}")


class Token(BaseModel):
    access_token: str
    token_type: str


class TokenData(BaseModel):
    id: Optional[str] = None
