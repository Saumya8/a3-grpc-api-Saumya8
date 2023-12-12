import os
import sys
import unittest
from unittest.mock import Mock

import grpc

sys.path.append(os.path.join(os.path.dirname(__file__), '..', 'client'))

from reddit_client import RedditClient

class MockPostResponse:
    def __init__(self, id=None):
        self.id = id

class MockCommentsResponse:
    def __init__(self, comments):
        self.comments = comments

class MockComment:
    def __init__(self, comment_id):
        self.comment_id = comment_id

# The tests
class TestRetrieveAndExpand(unittest.TestCase):

    def test_no_post(self):
        # Create a mock client with a non-existent post
        mock_client = Mock()
        mock_client.retrieve_post_content.return_value = MockPostResponse()
        result = RedditClient.retrieve_and_expand(mock_client, 'nonexistent_post')
        self.assertIsNone(result)

    def test_no_comments(self):
        # Mock client with a post that has no comments
        mock_client = Mock()
        mock_client.retrieve_post_content.return_value = MockPostResponse(id='post1')
        mock_client.retrieve_top_n_comments.return_value = MockCommentsResponse([])
        result = RedditClient.retrieve_and_expand(mock_client, 'post1')
        self.assertIsNone(result)

    def test_no_replies(self):
        mock_client = Mock()
        mock_client.retrieve_post_content.return_value = MockPostResponse(id='post1')
        mock_client.retrieve_top_n_comments.return_value = MockCommentsResponse([MockComment('comment1')])
        mock_client.expand_comment_branch.return_value = MockCommentsResponse([MockComment('comment1')])
        result = RedditClient.retrieve_and_expand(mock_client, 'post1')
        self.assertIsNone(result)

    def test_with_replies(self):
        mock_client = Mock()
        mock_client.retrieve_post_content.return_value = MockPostResponse(id='post1')
        mock_client.retrieve_top_n_comments.return_value = MockCommentsResponse([MockComment('comment1')])
        mock_client.expand_comment_branch.return_value = MockCommentsResponse([MockComment('comment1'), MockComment('reply1')])
        result = RedditClient.retrieve_and_expand(mock_client, 'post1')
        self.assertEqual(result.comment_id, 'reply1')
    
    def test_multiple_comments_same_upvotes(self):
        # Mock client with multiple comments having the same highest upvotes
        mock_client = Mock()
        mock_client.retrieve_post_content.return_value = MockPostResponse(id='post1')
        # Create comments with the same upvotes
        comments = [MockComment('comment1'), MockComment('comment2'), MockComment('comment3')]
        mock_client.retrieve_top_n_comments.return_value = MockCommentsResponse(comments)
        # Simulate that there are replies under the most upvoted comment
        mock_client.expand_comment_branch.return_value = MockCommentsResponse([MockComment('comment1'), MockComment('reply1')])
        result = RedditClient.retrieve_and_expand(mock_client, 'post1')
        self.assertIn(result.comment_id, ['comment1', 'reply1', 'comment2', 'comment3'])
        
    def test_error_expanding_comment(self):
        # Mock client with an error when expanding the comment
        mock_client = Mock()
        mock_client.retrieve_post_content.return_value = MockPostResponse(id='post1')
        mock_client.retrieve_top_n_comments.return_value = MockCommentsResponse([MockComment('comment1')])
        # Simulate an error when expanding the comment
        mock_client.expand_comment_branch.side_effect = grpc.RpcError("Error expanding comment")
        result = RedditClient.retrieve_and_expand(mock_client, 'post1')
        self.assertIsNone(result)
        
    def test_error_retrieving_top_comments(self):
        # Mock client with an error when retrieving top comments
        mock_client = Mock()
        mock_client.retrieve_post_content.return_value = MockPostResponse(id='post1')
        # Simulate an error when retrieving top comments
        mock_client.retrieve_top_n_comments.side_effect = grpc.RpcError("Error retrieving top comments")
        result = RedditClient.retrieve_and_expand(mock_client, 'post1')
        self.assertIsNone(result)

if __name__ == '__main__':
    unittest.main()
