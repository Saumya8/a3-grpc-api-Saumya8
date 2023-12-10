import grpc
from proto import reddit_pb2
from proto import reddit_pb2_grpc

class RedditClient:
    def __init__(self, host, port):
        self.channel = grpc.insecure_channel(f"{host}:{port}")
        self.stub = reddit_pb2_grpc.RedditServiceStub(self.channel)

    def create_post(self, title, text, subreddit_id):
        post = reddit_pb2.Post(title=title, text=text, subreddit_id=subreddit_id)
        return self.stub.CreatePost(post)

    def upvote_post(self, post_id):
        print(f"Upvoting post with ID: {post_id}")
        request = reddit_pb2.UpvoteDownvoteRequest(item_id=post_id, upvote=True)
        return self.stub.UpvoteDownvotePost(request)
    
    def downvote_post(self, post_id):
        request = reddit_pb2.UpvoteDownvoteRequest(item_id=post_id, upvote=False)
        return self.stub.UpvoteDownvotePost(request)

    def retrieve_post_content(self, post_id):
        request = reddit_pb2.PostRequest(post_id=post_id)
        return self.stub.RetrievePostContent(request)

    def create_comment(self, author, parent_id, text):
        comment = reddit_pb2.Comment(author=author, parent_id=parent_id, text=text)
        return self.stub.CreateComment(comment)

    def upvote_comment(self, comment_id):
        request = reddit_pb2.UpvoteDownvoteRequest(item_id=comment_id, upvote=True)
        return self.stub.UpvoteDownvoteComment(request)

    def downvote_comment(self, comment_id):
        request = reddit_pb2.UpvoteDownvoteRequest(item_id=comment_id, upvote=False)
        return self.stub.UpvoteDownvoteComment(request)

    def retrieve_top_n_comments(self, post_id, n):
        request = reddit_pb2.TopNCommentsRequest(post_id=post_id, n=n)
        return self.stub.RetrieveTopNComments(request)

    def expand_comment_branch(self, comment_id, n):
        request = reddit_pb2.ExpandCommentBranchRequest(comment_id=comment_id, n=n)
        return self.stub.ExpandCommentBranch(request)

    # Add Monitor Updates
    def monitor_updates(self, post_id, comment_ids):
        request = reddit_pb2.MonitorUpdatesRequest(post_id=post_id, comment_ids=comment_ids)
        return self.stub.MonitorUpdates(request)

    def close(self):
        self.channel.close()


if __name__ == "__main__":
    client = RedditClient("localhost", 50051)
    post = client.create_post("Example Title", "This is a test post", 1)
    
    # Create a Post
    print(f"Created Post: {post.title}")
    
    # Upvote a Post
    upvoted_post = client.upvote_post(post.id)
    print(f"Upvoted Post: {upvoted_post.title}, New Score: {upvoted_post.score}")
    
    # Create a comment
    comment = client.create_comment("user123", post.id, "This is a comment")
    print(f"Created Comment: {comment.comment_id} by {comment.author} - '{comment.text}'")

    # Upvote the comment
    upvoted_comment = client.upvote_comment(comment.comment_id)
    print(f"Upvoted Comment: {upvoted_comment.comment_id}, New Score: {upvoted_comment.score}")

    # Downvote the comment
    downvoted_comment = client.downvote_comment(comment.comment_id)
    print(f"Downvoted Comment: {downvoted_comment.comment_id}, New Score: {downvoted_comment.score}")
    
    # Retrieve Post Content
    retrieved_post = client.retrieve_post_content(post.id)
    print(f"Retrieved Post Content: {retrieved_post.title}")
    
    # Create multiple comments
    comment1 = client.create_comment("user1", post.id, "This is the first comment")
    comment2 = client.create_comment("user2", post.id, "This is the second comment")
    comment3 = client.create_comment("user3", post.id, "This is the third comment")

    # Create replies to the first comment
    reply1 = client.create_comment("user4", comment1.comment_id, "This is first reply to the first comment")
    reply2 = client.create_comment("user5", comment1.comment_id, "Second reply to the first comment")

    # Upvote comments and replies to simulate varying scores
    client.upvote_comment(comment1.comment_id)
    client.upvote_comment(comment1.comment_id)  # Upvoted twice
    client.upvote_comment(comment2.comment_id)
    client.downvote_comment(comment3.comment_id)  # Downvoted
    client.upvote_comment(reply1.comment_id)
    client.upvote_comment(reply2.comment_id)
    client.upvote_comment(reply2.comment_id)  # Upvoted twice
    client.upvote_comment(reply2.comment_id)  # Upvoted thrice
    
    # Retrieve Top N Comments
    top_comments = client.retrieve_top_n_comments(post.id, 2)
    print("Top Comments:")
    for idx, comment in enumerate(top_comments.comments):
        has_reply = "Yes" if top_comments.has_replies[idx] else "No"
        print(f" - {comment.comment_id}: '{comment.text}', Score: {comment.score}, Has Replies: {has_reply}")
    
    # Expand Comment Branch for the first comment
    expanded_comments = client.expand_comment_branch(comment1.comment_id, 2)
    print("Expanded Comment Branch for the first comment:")
    for expanded_comment in expanded_comments.comments:
        print(f" - {expanded_comment.comment_id}: '{expanded_comment.text}', Score: {expanded_comment.score}")
    
    # # Retrieve Top N Comments
    # top_comments = client.retrieve_top_n_comments(post.id, 3)
    # print("Top Comments:")
    # for comment in top_comments.comments:
    #     print(f" - {comment.comment_id}: {comment.text}")
        
    # top_comments = client.retrieve_top_n_comments("post_id_here", 5)
    # comment_branch = client.expand_comment_branch("comment_id_here", 3)
    # updates_stream = client.monitor_updates("post_id_here", ["comment_id1", "comment_id2"])

    # for update in updates_stream:
    #     print(f"Update: {update}")
    
    # Monitor Updates every second - Extra Credit
    print("Monitoring Updates:")
    try:
        updates_stream = client.monitor_updates(post.id, [comment.comment_id])
        for update in updates_stream:
            print(f"Update: {update.item_id}, New Score: {update.new_score}")
    except grpc.RpcError as e:
        print(f"Stream closed: {e}")
    client.close()
