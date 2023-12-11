import sys
import os
import unittest
from unittest.mock import MagicMock
import grpc

import pytest
sys.path.append(os.path.join(os.path.dirname(__file__), '..', 'client'))

from reddit_client import RedditClient

@pytest.fixture
def reddit_client():
    return RedditClient()


def get_most_upvoted_reply_under_top_comment(client, post_id):
    # Retrieve the post (optional, depending on whether you need details from the post itself)
    post = client.retrieve_post_content(post_id)
    if not post or not post.title:  # Check if post exists
        return None

    # Retrieve the top comment of the post
    top_comments = client.retrieve_top_n_comments(post_id, 1)
    if not top_comments.comments:
        return None  # No comments found

    top_comment = top_comments.comments[0]

    # Expand the most upvoted comment
    expanded_comments = client.expand_comment_branch(top_comment.comment_id, 1)
    if not expanded_comments.comments or len(expanded_comments.comments) <= 1:
        return None  # No replies found

    # The first comment is the top comment itself, so the second one (if exists) will be the most upvoted reply
    return expanded_comments.comments[1]



def test_get_most_upvoted_reply_under_top_comment():
    # Create a mock client instance
    mock_client = MagicMock(spec=RedditClient)

    # Mock the responses for each method called in the function
    mock_client.retrieve_post_content.return_value = MagicMock(title="Mock Post", id="1")
    mock_client.retrieve_top_n_comments.return_value = MagicMock(comments=[MagicMock(comment_id="1")])
    mock_client.expand_comment_branch.return_value = MagicMock(comments=[MagicMock(comment_id="1"), MagicMock(comment_id="2", text="Mock Reply")])

    # Call the function with the mock client
    most_upvoted_reply = get_most_upvoted_reply_under_top_comment(mock_client, "1")

    # Assert that the most upvoted reply is as expected
    assert most_upvoted_reply.comment_id == "2"
    assert most_upvoted_reply.text == "Mock Reply"
    
    
def test_create_post():
    #mock_client = MagicMock(spec=RedditClient)
    #mock_client.create_post.return_value = MagicMock(title="Test Post", text="This is a test", subreddit_id=1)
    reddit_client = RedditClient("localhost", 50051)
    response = reddit_client.create_post(title="Test Post", text="This is a test", subreddit_id=1)
    assert response.title == "Test Post"
    assert response.text == "This is a test"
    assert response.subreddit_id == 1
    
def test_upvote_post():
    #mock_reddit_client.upvote_post.return_value = MagicMock(score=1)
    reddit_client = RedditClient("localhost", 50051)
    post = reddit_client.create_post(title="Test Post", text="This is a test", subreddit_id=1)

    response = reddit_client.upvote_post(post.id)
    assert response.score == 1
    
def test_downvote_post():
    #mock_reddit_client.upvote_post.return_value = MagicMock(score=1)
    reddit_client = RedditClient("localhost", 50051)
    post = reddit_client.create_post(title="Test Post", text="This is a test", subreddit_id=1)

    response = reddit_client.downvote_post(post.id)
    assert response.score == -1

def test_create_comment():
    #mock_reddit_client.create_comment.return_value = mock_comment
    reddit_client = RedditClient("localhost", 50051)
    post = reddit_client.create_post(title="Test Post", text="This is a test", subreddit_id=1)

    response = reddit_client.create_comment("user1", post.id, "Test Comment")
    assert response.author == "user1"
    assert response.text == "Test Comment"

def test_upvote_comment():
    reddit_client = RedditClient("localhost", 50051)
    post = reddit_client.create_post(title="Test Post", text="This is a test", subreddit_id=1)

    comment = reddit_client.create_comment("user1", post.id, "Test Comment")

    response = reddit_client.upvote_comment(comment.comment_id)
    assert response.score == 1
    
def test_downvote_comment():
    reddit_client = RedditClient("localhost", 50051)
    post = reddit_client.create_post(title="Test Post", text="This is a test", subreddit_id=1)

    comment = reddit_client.create_comment("user1", post.id, "Test Comment")

    response = reddit_client.downvote_comment(comment.comment_id)
    assert response.score == -1

def test_retrieve_top_n_comments():
    reddit_client = RedditClient("localhost", 50051)
    post = reddit_client.create_post(title="Test Post", text="This is a test", subreddit_id=1)

    # Create comment 1 with score 5
    comment1 = reddit_client.create_comment("user1", post.id, "Test Comment 1")
    reddit_client.upvote_comment(comment1.comment_id) # Score = 1
    reddit_client.upvote_comment(comment1.comment_id) # Score = 2
    reddit_client.upvote_comment(comment1.comment_id) # Score = 3
    reddit_client.upvote_comment(comment1.comment_id) # Score = 4
    response1 = reddit_client.upvote_comment(comment1.comment_id) # Score = 5
    
    assert response1.score == 5
    
    # Create comment 2 with score -1
    comment2 = reddit_client.create_comment("user2", post.id, "Test Comment 2")
    reddit_client.downvote_comment(comment2.comment_id) # Score = -1
    reddit_client.downvote_comment(comment2.comment_id) # Score = -2
    reddit_client.upvote_comment(comment2.comment_id) # Score -1
    
    # Create comment 3 with score 3
    comment3 = reddit_client.create_comment("user3", post.id, "Test Comment 3")
    reddit_client.upvote_comment(comment3.comment_id) # Score = 1
    reddit_client.upvote_comment(comment3.comment_id) # Score = 2
    reddit_client.upvote_comment(comment3.comment_id) # Score = 3
    
    
    # mock_comment1 = MagicMock(comment_id="1", author="user1", text="Test Comment 1", score=5)
    # mock_comment2 = MagicMock(comment_id="2", author="user2", text="Test Comment 2", score=3)
    
    # Mock the response to simulate retrieving top N comments
    # mock_reddit_client.retrieve_top_n_comments.return_value = MagicMock(comments=[mock_comment1, mock_comment2])
    
    response = reddit_client.retrieve_top_n_comments(post.id, 2)
    assert len(response.comments) == 2
    assert response.comments[0].comment_id == comment1.comment_id
    assert response.comments[1].comment_id == comment3.comment_id
    
    
def test_expand_comment_branch():
    # mock_reply = MagicMock(comment_id="3", author="user3", text="Test Reply", score=4)
    
    reddit_client = RedditClient("localhost", 50051)
    post = reddit_client.create_post(title="Test Post", text="This is a test", subreddit_id=1)

    # Create comment 1 with score 5
    comment1 = reddit_client.create_comment("user1", post.id, "Test Comment 1")
    reddit_client.upvote_comment(comment1.comment_id) # Score = 1
    reddit_client.upvote_comment(comment1.comment_id) # Score = 2
    reddit_client.upvote_comment(comment1.comment_id) # Score = 3
    reddit_client.upvote_comment(comment1.comment_id) # Score = 4
    response1 = reddit_client.upvote_comment(comment1.comment_id) # Score = 5
    
    assert response1.score == 5
    
    # Create reply comment 2 with score -1
    comment2 = reddit_client.create_comment("user2", comment1.comment_id, "Test Reply 1")
    reddit_client.downvote_comment(comment2.comment_id) # Score = -1
    reddit_client.downvote_comment(comment2.comment_id) # Score = -2
    reddit_client.upvote_comment(comment2.comment_id) # Score -1
    
    # Create reply comment 3 with score 3
    comment3 = reddit_client.create_comment("user3", comment1.comment_id, "Test Reply 2")
    reddit_client.upvote_comment(comment3.comment_id) # Score = 1
    reddit_client.upvote_comment(comment3.comment_id) # Score = 2
    reddit_client.upvote_comment(comment3.comment_id) # Score = 3

    # Mock the response to simulate expanding a comment branch
    #mock_reddit_client.expand_comment_branch.return_value = MagicMock(comments=[mock_comment1, mock_reply])

    response = reddit_client.expand_comment_branch(comment1.comment_id, 2)
    assert len(response.comments) == 3
    # print(response.comments[0].comment_id)
    # print(response.comments[1].comment_id)
    # print(comment2)
    # print(comment3)
    assert response.comments[0].comment_id == comment1.comment_id
    assert response.comments[1].comment_id == comment3.comment_id # As score is higher, comment pushed to top
    assert response.comments[2].comment_id == comment2.comment_id # As score is low, comment pushed to bottom

# For Monitor Update, it update randomly, can't test
# def test_monitor_updates():
#     reddit_client = RedditClient("localhost", 50051)
#     post = reddit_client.create_post(title="Test Post", text="This is a test", subreddit_id=1)

#     # Create comment 1 with score 5
#     comment1 = reddit_client.create_comment("user1", post.id, "Test Comment 1")
#     reddit_client.upvote_comment(comment1.comment_id) # Score = 1
#     reddit_client.upvote_comment(comment1.comment_id) # Score = 2
#     reddit_client.upvote_comment(comment1.comment_id) # Score = 3
#     reddit_client.upvote_comment(comment1.comment_id) # Score = 4
#     response1 = reddit_client.upvote_comment(comment1.comment_id) # Score = 5
    
#     current_score = 0
#     assert response1.score == 5
#     mock_update = MagicMock(item_id="1", new_score=10)

#     try:
#         updates_stream = reddit_client.monitor_updates(post.id, [comment1.comment_id])
#         for update in updates_stream:
#             current_score += 1
#             assert update.new_score == 6
#             print(f"Update: {update.item_id}, New Score: {update.new_score}")
#     except grpc.RpcError as e:
#         print(f"Stream closed: {e}")
    # Mock the response to simulate monitoring updates
    
    
    #mock_reddit_client.monitor_updates.return_value = [mock_update]

    # updates = list(mock_reddit_client.monitor_updates("1", ["1"]))
    # assert len(updates) == 1
    # assert updates[0].item_id == "1"
    # assert updates[0].new_score == 10



# Run the test
if __name__ == "__main__":
    
    client1 = RedditClient("localhost", 50051)
    # Random Test
    test_get_most_upvoted_reply_under_top_comment()
    
    # Create Post
    test_create_post()
    
    # Upvote and Downvote Post
    test_upvote_post()
    test_downvote_post()
    
    # Create Comment
    test_create_comment()
    
    # Upvote and downvote  Comment
    test_upvote_comment()
    test_downvote_comment()
    
    # Retrive Top n Comment
    test_retrieve_top_n_comments()
    
    # Expand Comment branch to n number of comments
    test_expand_comment_branch()
    
    print("Test passed")
