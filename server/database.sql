CREATE TABLE users (
    user_id TEXT PRIMARY KEY
);

CREATE TABLE subreddits (
    subreddit_id INTEGER PRIMARY KEY AUTOINCREMENT,
    name TEXT NOT NULL,
    visibility INTEGER NOT NULL,
    tags TEXT  -- JSON array of tags or a comma-separated list
);

CREATE TABLE posts (
    post_id INTEGER PRIMARY KEY AUTOINCREMENT,
    title TEXT NOT NULL,
    text TEXT NOT NULL,
    video_url TEXT,
    image_url TEXT,
    author TEXT,
    score INTEGER NOT NULL,
    state INTEGER NOT NULL,
    publication_date INTEGER NOT NULL,
    subreddit_id INTEGER NOT NULL,
    FOREIGN KEY (subreddit_id) REFERENCES subreddits(subreddit_id)
);

CREATE TABLE comments (
    comment_id INTEGER PRIMARY KEY AUTOINCREMENT,
    author TEXT NOT NULL,
    score INTEGER NOT NULL,
    state INTEGER NOT NULL,
    publication_date INTEGER NOT NULL,
    parent_id INTEGER,
    post_id INTEGER,
    FOREIGN KEY (post_id) REFERENCES posts(post_id)
);
