from flask import Flask, request, jsonify
import grpc
from proto import reddit_pb2
from proto import reddit_pb2_grpc
from reddit_client import RedditClient

app = Flask(__name__)
client = RedditClient("localhost", 50051)

# Create a Post
@app.route('/create_post', methods=['POST'])
def create_post():
    data = request.get_json()
    title = data.get('title')
    text = data.get('text')
    subreddit_id = data.get('subreddit_id')
    post = client.create_post(title, text, subreddit_id)
    return jsonify({'message': 'Post created successfully', 'post_id': post.id})

# Upvote a Post
@app.route('/upvote_post/<post_id>', methods=['POST'])
def upvote_post(post_id):
    upvoted_post = client.upvote_post(post_id)
    return jsonify({'message': 'Post upvoted successfully', 'post_title': upvoted_post.title, 'new_score': upvoted_post.score})

# Downvote a Post
@app.route('/downvote_post/<post_id>', methods=['POST'])
def downvote_post(post_id):
    downvoted_post = client.downvote_post(post_id)
    return jsonify({'message': 'Post downvoted successfully', 'post_title': downvoted_post.title, 'new_score': downvoted_post.score})

# Retrieve Post Content
@app.route('/retrieve_post_content/<post_id>', methods=['GET'])
def retrieve_post_content(post_id):
    post = client.retrieve_post_content(post_id)
    if post:
        return jsonify({'post_title': post.title, 'post_text': post.text})
    else:
        return jsonify({'error': 'Post not found'}), 404

# Create a Comment
@app.route('/create_comment', methods=['POST'])
def create_comment():
    data = request.get_json()
    author = data.get('author')
    parent_id = data.get('parent_id')
    text = data.get('text')
    comment = client.create_comment(author, parent_id, text)
    return jsonify({'message': 'Comment created successfully', 'comment_id': comment.comment_id})

# Upvote a Comment
@app.route('/upvote_comment/<comment_id>', methods=['POST'])
def upvote_comment(comment_id):
    upvoted_comment = client.upvote_comment(comment_id)
    return jsonify({'message': 'Comment upvoted successfully', 'comment_id': upvoted_comment.comment_id, 'new_score': upvoted_comment.score})

# Downvote a Comment
@app.route('/downvote_comment/<comment_id>', methods=['POST'])
def downvote_comment(comment_id):
    downvoted_comment = client.downvote_comment(comment_id)
    return jsonify({'message': 'Comment downvoted successfully', 'comment_id': downvoted_comment.comment_id, 'new_score': downvoted_comment.score})

# Retrieve Top N Comments
@app.route('/retrieve_top_n_comments/<post_id>/<int:n>', methods=['GET'])
def retrieve_top_n_comments(post_id, n):
    top_comments = client.retrieve_top_n_comments(post_id, n)
    if top_comments:
        comments_data = [{'comment_id': comment.comment_id, 'text': comment.text, 'score': comment.score} for comment in top_comments.comments]
        return jsonify({'top_comments': comments_data})
    else:
        return jsonify({'error': 'Comments not found'}), 404

# Expand Comment Branch
@app.route('/expand_comment_branch/<comment_id>/<int:n>', methods=['GET'])
def expand_comment_branch(comment_id, n):
    expanded_comments = client.expand_comment_branch(comment_id, n)
    if expanded_comments:
        comments_data = [{'comment_id': comment.comment_id, 'text': comment.text, 'score': comment.score} for comment in expanded_comments.comments]
        return jsonify({'expanded_comments': comments_data})
    else:
        return jsonify({'error': 'Expanded comments not found'}), 404

# Monitor Updates (Extra Credit)
@app.route('/monitor_updates/<post_id>/<comment_id>', methods=['GET'])
def monitor_updates(post_id, comment_id):
    updates_stream = client.monitor_updates(post_id, [comment_id])
    updates_data = [{'item_id': update.item_id, 'new_score': update.new_score} for update in updates_stream]
    return jsonify({'updates': updates_data})


@app.route("/retrieve_most_upvoted_reply/<int:post_id>", methods=["GET"])
def retrieve_most_upvoted_reply(post_id):
    # Find the most upvoted comment
    most_upvoted_comment = None
    max_score = -1

    for comment in sample_comments:
        if comment["score"] > max_score:
            most_upvoted_comment = comment
            max_score = comment["score"]

    if most_upvoted_comment is None:
        # No comments found
        return jsonify({"message": "No comments or replies found under the most upvoted comment."}), 200

    if not most_upvoted_comment["replies"]:
        # No replies found
        return jsonify({"message": "No replies found under the most upvoted comment."}), 200

    # Find the most upvoted reply
    most_upvoted_reply = None
    max_reply_score = -1

    for reply in most_upvoted_comment["replies"]:
        if reply["score"] > max_reply_score:
            most_upvoted_reply = reply
            max_reply_score = reply["score"]

    return jsonify(most_upvoted_reply), 200

if __name__ == "__main__":
    app.run(debug=True)
