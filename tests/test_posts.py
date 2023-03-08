import pytest
from app.schemas import PostWithVotes, Post


def test_get_all_posts(authorized_client, test_posts):
    response = authorized_client.get("/posts")
    assert response.status_code == 200
    posts_response = response.json()
    assert isinstance(posts_response, list)
    posts = [PostWithVotes(**post) for post in posts_response]
    assert len(posts) == len(test_posts)
    assert {post.id for post in posts} == {post.id for post in test_posts}


def test_unauthorized_user_get_all_posts(client, test_posts):
    response = client.get("/posts")
    assert response.status_code == 401


def test_get_one_post(authorized_client, test_posts):
    response = authorized_client.get(f"/posts/{test_posts[0].id}")
    post = Post(**response.json())
    assert post.id == test_posts[0].id
    assert post.content == test_posts[0].content
    assert post.title == test_posts[0].title


def test_get_one_post_not_exist(authorized_client, test_posts):
    response = authorized_client.get(f"/posts/666")
    assert response.status_code == 404


def test_unauthorized_user_get_one_post(client, test_posts):
    response = client.get(f"/posts/{test_posts[0].id}")
    assert response.status_code == 401


@pytest.mark.parametrize(
    "title, content, published",
    [
        ("awesome new title", "awesome new content", True),
        ("fav pizza", "margherita", True),
        ("API", "fastapi", True),
    ],
)
def test_create_post(
    authorized_client, test_user, test_posts, title, content, published
):
    response = authorized_client.post(
        "/posts", json={"title": title, "content": content, "published": published}
    )
    post = Post(**response.json())
    assert response.status_code == 201
    assert post.title == title
    assert post.content == content
    assert post.published == published
    assert post.user_id == test_user["id"]


def test_create_post_default_published(
    authorized_client, test_user, test_posts
):
    response = authorized_client.post(
        "/posts", json={"title": "title", "content": "content"}
    )
    post = Post(**response.json())
    assert response.status_code == 201
    assert post.title == "title"
    assert post.content == "content"
    assert post.published == True
    assert post.user_id == test_user["id"]


def test_unauthorized_user_create_post(client, test_posts):
    response = client.post("/posts", json={"title": "title", "content": "content"})
    assert response.status_code == 401


def test_delete__post(authorized_client, test_user, test_posts):
    response = authorized_client.delete(f"posts/{test_posts[0].id}")
    assert response.status_code == 204


def test_unauthorized_user_delete_post(client, test_user, test_posts):
    response = client.delete(f"posts/{test_posts[0].id}")
    assert response.status_code == 401


def test_delete_inexistant_post(authorized_client, test_user, test_posts):
    response = authorized_client.delete("posts/666")
    assert response.status_code == 404


def test_delete_other_user_post(authorized_client, test_user, test_posts):
    pass