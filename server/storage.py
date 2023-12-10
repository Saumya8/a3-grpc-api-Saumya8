
from storage import Database

import sqlite3
from datetime import datetime
import proto.reddit_pb2 as reddit_pb2
import proto.reddit_pb2_grpc as reddit_pb2_grpc

class Database:
    def __init__(self, db_path):
        self.conn = sqlite3.connect(db_path)
        self.conn.row_factory = sqlite3.Row  # Enables column access by name

    def create_post(self, title, text, author, subreddit_id):
        cursor = self.conn.cursor()
        try:
            # Current timestamp as publication date
            publication_date = int(datetime.now().timestamp())

            # Insert post into the database
            cursor.execute("""
                INSERT INTO posts (title, text, author, score, state, publication_date, subreddit_id)
                VALUES (?, ?, ?, 0, ?, ?, ?)
            """, (title, text, author, reddit_pb2.PostState.POST_NORMAL, publication_date, subreddit_id))

            self.conn.commit()
            return cursor.lastrowid  # Return the ID of the created post
        except sqlite3.Error as e:
            print(f"SQLite error: {e}")
            return None

    def close(self):
        self.conn.close()

