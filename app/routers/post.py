from typing import List
from sqlalchemy import func
from sqlalchemy.orm import Session

from .. import models, schemas, oauth2
from ..database import get_db
from fastapi import HTTPException, status, Depends, APIRouter


router = APIRouter(prefix="/posts", tags=["Posts"])


@router.get("/", response_model=List[schemas.PostWithVotes])
def get_posts(
    db: Session = Depends(get_db),
    user: schemas.UserResponse = Depends(oauth2.get_current_user),
    limit: int = 10,
    skip: int = 0,
    search: str = "",
):
    query_posts = db.query(
        models.Post, func.count(models.Vote.post_id).label("votes")
    ).filter(models.Post.title.contains(search))
    join_with_votes = query_posts.join(
        models.Vote, models.Post.id == models.Vote.post_id, isouter=True
    )
    groupby_post = join_with_votes.group_by(models.Post.id)
    # NOTE If you want to have a User in the response, skip the subquery and change the response schema
    return db.query(groupby_post.limit(limit).offset(skip).subquery()).all()


# TODO Figure out when to use detail and when to use data
@router.get("/latest", response_model=schemas.Post)
def get_latest_post(
    db: Session = Depends(get_db),
    user: schemas.UserResponse = Depends(oauth2.get_current_user),
):  # This could also be a fastapi.Body
    max_id = db.query(func.max(models.Post.id)).first()[0]
    post = db.query(models.Post).filter(models.Post.id == max_id).first()
    if not post:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Post with id {id} was not found",
        )
    return post


@router.get(
    "/{id}", response_model=schemas.PostWithVotes
)  # path parameter, this has to be the last defined GET on posts/sthg
def get_post(
    id: int,
    db: Session = Depends(get_db),
    user: schemas.UserResponse = Depends(oauth2.get_current_user),
):
    query_posts = db.query(
        models.Post, func.count(models.Vote.post_id).label("votes")
    ).filter(models.Post.id == id)
    join_with_votes = query_posts.join(
        models.Vote, models.Post.id == models.Vote.post_id, isouter=True
    )
    groupby_post = join_with_votes.group_by(models.Post.id)
    post = db.query(groupby_post.subquery()).first()
    if not post:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Post with id {id} was not found",
        )
    return post



@router.post("/", status_code=status.HTTP_201_CREATED, response_model=schemas.Post)
def create_post(
    post: schemas.PostCreate,
    db: Session = Depends(get_db),
    user: schemas.UserResponse = Depends(oauth2.get_current_user),
):
    new_post = models.Post(
        **dict(post), user_id=user.id
    )  # TODO Give Post all the fields
    db.add(new_post)
    db.commit()
    db.refresh(new_post)
    return new_post


@router.delete("/{id}", status_code=status.HTTP_204_NO_CONTENT)
def delete_post(
    id: int,
    db: Session = Depends(get_db),
    user: schemas.UserResponse = Depends(oauth2.get_current_user),
):
    query_deleted_post = db.query(models.Post).filter(models.Post.id == id)
    deleted_post = query_deleted_post.first()
    if not deleted_post:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Post with id {id} was not found",
        )
    if deleted_post.user_id != user.id:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Not authorized to perform this operation",
        )
    query_deleted_post.delete(synchronize_session=False)
    db.commit()


# TODO Figure out how to update a post without having to re implement all its fields
@router.put("/{id}", status_code=status.HTTP_200_OK, response_model=schemas.Post)
def update_post(
    id: int,
    post: schemas.PostCreate,
    db: Session = Depends(get_db),
    user: schemas.UserResponse = Depends(oauth2.get_current_user),
):
    query_updated_post = db.query(models.Post).filter(models.Post.id == id)
    updated_post = query_updated_post.first()
    if not updated_post:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Post with id {id} was not found",
        )
    if updated_post.user_id != user.id:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Not authorized to perform this operation",
        )
    query_updated_post.update(dict(post), synchronize_session=False)
    db.commit()
    return query_updated_post.first()
