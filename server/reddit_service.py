import argparse

from concurrent import futures
import datetime
import os
import random
import sys
# from storage import Database
import uuid
import time
import threading
import logging
import grpc

sys.path.append(os.path.join(os.path.dirname(__file__), '..', 'proto'))
from proto import reddit_pb2
from proto import reddit_pb2_grpc

posts = {}  # Dictionary for posts
comments = {}  # Dictionary for comments
users = {
    "user1": reddit_pb2.User(user_id="user1"),
    "user2": reddit_pb2.User(user_id="user2"),
    "user3": reddit_pb2.User(user_id="user3"),
    "user4": reddit_pb2.User(user_id="user4"),
    "user5": reddit_pb2.User(user_id="user5"),
    } # Sample Dictionary for users
#logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')

# next_post_id = 1
# next_comment_id = 1


# For Monitorring Updates
def update_scores():
    while True:
        for post in posts.values():
            post.score += random.randint(-1, 1)  # Randomly increment or decrement score
        for comment in comments.values():
            comment.score += random.randint(-1, 1)
        time.sleep(5)  # Update scores every 5 seconds


class RedditService(reddit_pb2_grpc.RedditServiceServicer):
    
    #1. Create a Post
    def CreatePost(self, request, context):
        # Always grant to user therefore no check for user id required just a warning
        if request.author not in users:
            logging.warning(f"User {request.author} isn't in authenticated userbase.")
        
        try:
            post_id = str(uuid.uuid4())  # Generate a unique UUID
            new_post = reddit_pb2.Post(
                id=post_id,
                title=request.title,
                text=request.text,
                author=request.author,
                score=0,
                state=reddit_pb2.POST_NORMAL,
                publication_date=int(datetime.datetime.now().timestamp()),
                subreddit_id=request.subreddit_id
            )
            posts[post_id] = new_post  # Store the new post in the dictionary
            logging.info(f"Post created successfully: {request.title}")

            return new_post
        except Exception as e:
            logging.error(f"Failed to create post: {e}")

    # 2. Upvote or Downvote Post
    def UpvoteDownvotePost(self, request, context):
        try:
            post_id = request.item_id
            if post_id in posts:
                posts[post_id].score += 1 if request.upvote else -1
                logging.info(f"Post {request.item_id} {'upvoted' if request.upvote else 'downvoted'} successfully. New score {posts[post_id].score}.")
                return posts[post_id]
        
            logging.info(f"Post {request.item_id} not found.")

            return reddit_pb2.Post()  # Return an empty post if not found
        except Exception as e:
            logging.error(f"Failed to upvote/downvote post: {e}")

    # 3. Retrive Post Content
    def RetrievePostContent(self, request, context):
        try:
            post_id = request.post_id
            if post_id in posts:
                logging.info(f"Retrieving content for post: {post_id}")
                return posts[post_id]
            else:
                logging.warning(f"Post with ID {post_id} not found.")
                return reddit_pb2.Post()  # Return an empty post if not found
        except Exception as e:
            logging.error(f"Failed to retrieve post content: {e}")

    # 4. Create Comment
    def CreateComment(self, request, context):
        try: 
            #comment_id = f"c{len(comments) + 1}"  # Generate a unique comment ID
            comment_id = str(uuid.uuid4())  # Generate a unique UUID

            new_comment = reddit_pb2.Comment(
                comment_id=comment_id,
                author=request.author,
                score=0,
                state=reddit_pb2.COMMENT_NORMAL,
                publication_date=int(datetime.datetime.now().timestamp()),
                parent_id=request.parent_id,
                text=request.text
            )
            comments[comment_id] = new_comment  # Store the new comment in the dictionary
            logging.info(f"Comment created successfully: Comment ID {comment_id}, Author {request.author}")
            return new_comment
        except Exception as e:
            logging.error(f"Failed to create comment: {e}")

    # 4. Upvote or Downvote a Comment
    def UpvoteDownvoteComment(self, request, context):
        try:
            comment_id = request.item_id
            if comment_id in comments:
                comments[comment_id].score += 1 if request.upvote else -1
                logging.info(f"Comment {comment_id} {'upvoted' if request.upvote else 'downvoted'} successfully. New score {comments[comment_id].score}.")
                return comments[comment_id]
            else:
                logging.warning(f"Comment with ID {comment_id} not found.")
                return reddit_pb2.Comment()  # Return empty comment if not found
        except Exception as e:
            logging.error(f"Failed to upvote/downvote comment: {e}")

        # new_score = 1 if request.upvote else -1
        # return reddit_pb2.Comment(score=new_score)

    # 5. rerieve Top N comments
    def RetrieveTopNComments(self, request, context):
        try:
            post_comments = [
                comment for comment in comments.values() if comment.parent_id == request.post_id
            ]
            sorted_comments = sorted(post_comments, key=lambda c: c.score, reverse=True)[:request.n]
            has_replies = [any(c.parent_id == comment.comment_id for c in comments.values()) for comment in sorted_comments]
            logging.info(f"Retrieved top {request.n} comments for post {request.post_id}")
            return reddit_pb2.TopNCommentsResponse(comments=sorted_comments, has_replies=has_replies)
        except Exception as e:
            logging.error(f"Failed to retrieve top comments: {e}")
            # post_id = request.post_id
            # post_comments = [comment for comment in comments.values() if comment.parent_id == post_id]
            # sorted_comments = sorted(post_comments, key=lambda c: c.score, reverse=True)
            # top_comments = sorted_comments[:request.n]
            # has_replies = [False for _ in top_comments]  # Simplified
            # return reddit_pb2.TopNCommentsResponse(comments=top_comments, has_replies=has_replies)

    # 6. Expand a Comment Branch
    def ExpandCommentBranch(self, request, context):
        try:
            comment_branch = []
            main_comment = comments.get(request.comment_id)
            if main_comment:
                comment_branch.append(main_comment)
                child_comments = [comment for comment in comments.values() if comment.parent_id == main_comment.comment_id]
                sorted_children = sorted(child_comments, key=lambda c: c.score, reverse=True)[:request.n]
                comment_branch.extend(sorted_children)
            logging.info(f"Expanded comment branch for comment {request.comment_id}")
            return reddit_pb2.ExpandCommentBranchResponse(comments=comment_branch)
        except Exception as e:
            logging.error(f"Failed to expand comment branch: {e}")
        # comments = [reddit_pb2.Comment(author="user", score=i) for i in range(request.n)]
        # return reddit_pb2.ExpandCommentBranchResponse(comments=comments)
        # parent_comment_id = request.comment_id
        # child_comments = [comment for comment in comments.values() if comment.parent_id == parent_comment_id]
        # sorted_comments = sorted(child_comments, key=lambda c: c.score, reverse=True)
        # branch_comments = sorted_comments[:request.n]
        # return reddit_pb2.ExpandCommentBranchResponse(comments=branch_comments)
    
    
    
    # 7. Extra - Monitor Updates
    def MonitorUpdates(self, request, context):
        last_post_score = None
        last_comment_scores = {}

        while True:
            # Check for post score update
            if request.post_id in posts:
                post = posts[request.post_id]
                if last_post_score != post.score:
                    yield reddit_pb2.ScoreUpdate(
                        item_id=post.id, 
                        new_score=post.score
                    )
                    last_post_score = post.score

            # Check for comment score updates
            for comment_id in request.comment_ids:
                if comment_id in comments:
                    comment = comments[comment_id]
                    if last_comment_scores.get(comment_id) != comment.score:
                        yield reddit_pb2.ScoreUpdate(
                            item_id=comment.comment_id, 
                            new_score=comment.score
                        )
                        last_comment_scores[comment_id] = comment.score

            time.sleep(1)  # Check for updates every second
        
        # post_id = request.post_id
        # comment_ids = request.comment_ids

        # try:
        #     while True:
        #         # Simulate a score update
        #         updated_post_score = random.randint(-10, 10)
        #         yield reddit_pb2.ScoreUpdate(item_id=post_id, new_score=updated_post_score)

        #         for comment_id in comment_ids:
        #             updated_comment_score = random.randint(-10, 10)
        #             yield reddit_pb2.ScoreUpdate(item_id=comment_id, new_score=updated_comment_score)

        #         time.sleep(5)  # Wait for 5 seconds before sending the next update
        # except KeyboardInterrupt:
        #     pass

def serve(host, port):
    server = grpc.server(futures.ThreadPoolExecutor(max_workers=10))
    reddit_pb2_grpc.add_RedditServiceServicer_to_server(RedditService(), server)
    server.add_insecure_port(f'{host}:{port}')
    server.start()
    print(f'Server running on {host}:{port}')
    server.wait_for_termination()
    
if __name__ == '__main__':
    parser = argparse.ArgumentParser(description='gRPC Reddit Clone Server')
    parser.add_argument('--host', default='localhost', type=str, help='Host to run gRPC server on')
    parser.add_argument('--port', default=50051, type=int, help='Port to run gRPC server on')
    args = parser.parse_args()
    logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')


    # Start the background thread for score updating
    threading.Thread(target=update_scores, daemon=True).start()

    # Start the gRPC server with the provided host and port
    serve(args.host, args.port)
    
    
    # Extra - Database 
    # db = Database('storage.db')

    # server = grpc.server(futures.ThreadPoolExecutor(max_workers=10))
    # reddit_pb2_grpc.add_RedditServiceServicer_to_server(RedditService(db), server)
    # server.add_insecure_port('[::]:50051')
    # server.start()
    # print("Server started, listening on port 50051.")
    # server.wait_for_termination()
    
    
    # server = grpc.server(futures.ThreadPoolExecutor(max_workers=10))
    # reddit_pb2_grpc.add_RedditServiceServicer_to_server(RedditService(), server)
    # server.add_insecure_port('[::]:50051')
    # server.start()
    # server.wait_for_termination()

# if __name__ == '__main__':
#     parser = argparse.ArgumentParser(description='gRPC Reddit Clone Server')
#     parser.add_argument('--host', default='localhost', type=str, help='Host to run gRPC server on')
#     parser.add_argument('--port', default=50051, type=int, help='Port to run gRPC server on')
#     args = parser.parse_args()

#     threading.Thread(target=update_scores, daemon=True).start()
#     serve(args.host, args.port)
