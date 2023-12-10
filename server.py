from concurrent import futures
import grpc
import your_service_pb2
import your_service_pb2_grpc
import uuid


# Dummy data storage
posts = {}

comments = {}  # Dummy storage for comments

class RedditService(your_service_pb2_grpc.RedditServiceServicer):

    def CreatePost(self, request, context):
        post_id = str(len(posts) + 1)  # Simple ID generation
        new_post = your_service_pb2.Post(
            id=post_id,
            author=request.author,
            title=request.title,
            content=request.content,
            score=0,
            subreddit_id=request.subreddit_id
        )
        posts[post_id] = new_post
        return your_service_pb2.CreatePostResponse(post=new_post)

    def VotePost(self, request, context):
        post = posts.get(request.entity_id)
        if not post:
            context.set_code(grpc.StatusCode.NOT_FOUND)
            context.set_details('Post not found')
            return your_service_pb2.VoteResponse()

        if request.upvote:
            post.score += 1
        else:
            post.score -= 1

        return your_service_pb2.VoteResponse(new_score=post.score)

    def GetPost(self, request, context):
        post = posts.get(request.post_id)
        if not post:
            context.set_code(grpc.StatusCode.NOT_FOUND)
            context.set_details('Post not found')
            return your_service_pb2.GetPostResponse()
        
        return your_service_pb2.GetPostResponse(post=post)

    def RetrievePostContent(self, request, context):
        post = posts.get(request.post_id)
        if post is None:
            context.abort(grpc.StatusCode.NOT_FOUND, 'Post not found')
        return your_service_pb2.RetrievePostContentResponse(title=post.title, content=post.content)

    def UpvotePost(self, request, context):
        post = posts.get(request.entity_id)
        if post is None:
            context.abort(grpc.StatusCode.NOT_FOUND, 'Post not found')

        post.score += 1 if request.upvote else -1
        return your_service_pb2.VoteResponse(new_score=post.score)

    def CreateComment(self, request, context):
        comment_id = str(len(comments) + 1)  # Assuming 'comments' is a global dictionary
        new_comment = your_service_pb2.Comment(
            id=comment_id,
            author=request.author,
            parent_id=request.parent_id,
            content=request.content,
            score=0,
            status=your_service_pb2.Comment.NORMAL,
            publication_date=str(datetime.now())
        )
        comments[comment_id] = new_comment
        return your_service_pb2.CreateCommentResponse(comment=new_comment)

    def UpvoteComment(self, request, context):
        comment = comments.get(request.entity_id)
        if not comment:
            context.abort(grpc.StatusCode.NOT_FOUND, 'Comment not found')

        comment.score += 1 if request.upvote else -1
        return your_service_pb2.VoteResponse(new_score=comment.score)

    def GetTopComments(self, request, context):
        post_comments = [comment for comment in comments.values() if comment.parent_id == request.post_id]
        sorted_comments = sorted(post_comments, key=lambda x: x.score, reverse=True)
        top_comments = sorted_comments[:request.number_of_comments]
        return your_service_pb2.GetTopCommentsResponse(comments=top_comments)

    def ExpandCommentBranch(self, request, context):
        def get_top_replies(comment_id, n):
            replies = [comment for comment in comments.values() if comment.parent_id == comment_id]
            sorted_replies = sorted(replies, key=lambda x: x.score, reverse=True)
            return sorted_replies[:n]

        parent_comment = comments.get(request.comment_id)
        if not parent_comment:
            context.abort(grpc.StatusCode.NOT_FOUND, 'Comment not found')

        top_replies = get_top_replies(request.comment_id, request.number_of_comments)
        reply_branches = [your_service_pb2.CommentBranch(
            parent_comment=reply, 
            top_comments=get_top_replies(reply.id, request.number_of_comments)
        ) for reply in top_replies]

        return your_service_pb2.ExpandCommentBranchResponse(
            comment_branch=your_service_pb2.CommentBranch(
                parent_comment=parent_comment, 
                top_comments=top_replies
            ),
            reply_branches=reply_branches
        )
    
    def MonitorUpdates(self, request_iterator, context):
        for request in request_iterator:
            post_id = request.post_id
            comment_ids = request.comment_ids

            while not context.is_active():  # Loop until the client disconnects
                time.sleep(5)  # Wait for 5 seconds before sending each update

                # Simulating a score update
                updated_score = random.randint(1, 100)  # Random score for demonstration

                # Send an update for the post
                yield your_service_pb2.UpdateStream(entity_id=post_id, new_score=updated_score)

                # Send updates for each comment
                for comment_id in comment_ids:
                    updated_score = random.randint(1, 100)  # Random score for each comment
                    yield your_service_pb2.UpdateStream(entity_id=comment_id, new_score=updated_score)

    ## Need to rest

def serve():
    server = grpc.server(futures.ThreadPoolExecutor(max_workers=10))
    your_service_pb2_grpc.add_RedditServiceServicer_to_server(RedditService(), server)
    server.add_insecure_port('[::]:50051')
    server.start()
    print("Server started at port 50051")
    server.wait_for_termination()

if __name__ == '__main__':
    serve()
