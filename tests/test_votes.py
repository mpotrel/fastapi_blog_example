import pytest


def get_post_votes(user_client, post_id):
    return user_client.get(f"/posts/{post_id}").json()["votes"]


def get_second_user_post_id(users, posts):
    second_user_id = users[1]["id"]
    return [post for post in posts if post.user_id == second_user_id][0].id


def test_vote(authorized_client, test_users, test_posts):
    second_user_post_id = get_second_user_post_id(test_users, test_posts)
    assert get_post_votes(authorized_client, second_user_post_id) == 0
    data = {"post_id": second_user_post_id, "dir": 1}
    response = authorized_client.post("/votes", json=data)
    assert response.status_code == 201
    assert response.json().get("message") == "Successfully upvoted post"
    assert get_post_votes(authorized_client, second_user_post_id) == 1


def test_upvote_twice(authorized_client, test_users, test_posts):
    second_user_post_id = get_second_user_post_id(test_users, test_posts)
    data = {"post_id": second_user_post_id, "dir": 1}
    authorized_client.post("/votes", json=data)  # First vote
    response = authorized_client.post("/votes", json=data)  # Second vote
    assert response.status_code == 409
    assert response.json().get("detail") == f"User {test_users[0]['id']} has already upvoted post {second_user_post_id}"
    assert get_post_votes(authorized_client, second_user_post_id) == 1


def test_remove_upvote(authorized_client, test_users, test_posts):
    second_user_post_id = get_second_user_post_id(test_users, test_posts)
    assert get_post_votes(authorized_client, second_user_post_id) == 0
    data = {"post_id": second_user_post_id, "dir": 1}
    authorized_client.post("/votes", json=data)  # Upvote
    assert get_post_votes(authorized_client, second_user_post_id) == 1
    data["dir"] = 0
    response = authorized_client.post("/votes", json=data) # Downvote
    assert get_post_votes(authorized_client, second_user_post_id) == 0
    assert response.status_code == 201
    assert response.json().get("message") == "Successfully removed upvote"


def test_downvote_twice(authorized_client, test_users, test_posts):
    second_user_post_id = get_second_user_post_id(test_users, test_posts)
    data = {"post_id": second_user_post_id, "dir": 1}
    authorized_client.post("/votes", json=data)  # Upvote
    data["dir"] = 0
    authorized_client.post("/votes", json=data) # Downvote
    response = authorized_client.post("/votes", json=data) # Downvote again
    assert get_post_votes(authorized_client, second_user_post_id) == 0
    assert response.status_code == 409
    assert response.json().get("detail") == f"User {test_users[0]['id']} has not upvoted post {second_user_post_id}"


def test_remove_upvote_without_vote(authorized_client, test_users, test_posts):
    second_user_post_id = get_second_user_post_id(test_users, test_posts)
    data = {"post_id": second_user_post_id, "dir": 0}
    response = authorized_client.post("/votes", json=data)
    assert get_post_votes(authorized_client, second_user_post_id) == 0
    assert response.status_code == 409
    assert response.json().get("detail") == f"User {test_users[0]['id']} has not upvoted post {second_user_post_id}"


@pytest.mark.parametrize("dir", [0, 1])
def test_unauthorized_vote(client, test_posts, dir):
    post_id = test_posts[0].id
    data = {"post_id": post_id, "dir": dir}
    response = client.post("/votes", json=data)
    assert response.status_code == 401


@pytest.mark.parametrize("dir", [0, 1])
def test_vote_non_existing_post(authorized_client, dir):
    fake_post_id = 666
    response = authorized_client.post("/votes", json={"post_id": fake_post_id, "dir": dir})
    assert response.status_code == 404
    assert response.json().get("detail") == f"Post with id {fake_post_id} was not found"


# Some adjustments need to be made to the pydantic validation of Vote
# @pytest.mark.parametrize("dir", [2, "a", True, False])
# def test_vote_non_accepted_dir(authorized_client, test_posts, dir):
#     data = {"post_id": test_posts[0].id, "dir": dir}
#     response = authorized_client.post("/votes", json=data)
#     print(response.status_code)
#     print(response.json())
