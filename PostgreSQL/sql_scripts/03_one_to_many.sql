-- =========================================================
-- 03 - ONE TO MANY RELATIONSHIP
-- Problem:
-- One user can have many posts.
-- We use foreign keys to connect tables.
-- =========================================================

CREATE TABLE posts (
    id SERIAL PRIMARY KEY,
    title TEXT NOT NULL,
    content TEXT,
    user_id INT REFERENCES users(id),  -- Foreign key
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

-- Insert example
INSERT INTO posts (title, user_id)
VALUES ('Learning SQL', 1);
