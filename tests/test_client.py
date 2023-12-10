import sys
import os
import unittest
from unittest.mock import MagicMock
sys.path.append(os.path.join(os.path.dirname(__file__), '..', 'client'))

from reddit_client import RedditClient

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

# Run the test
if __name__ == "__main__":
    test_get_most_upvoted_reply_under_top_comment()
    print("Test passed")
