-- =========================================================
-- 04 - JOIN & LEFT JOIN
-- Problem:
-- Data is stored in separate tables.
-- We need to combine them when querying.
-- =========================================================

-- INNER JOIN (only matched rows)
SELECT users.name, posts.title
FROM posts
JOIN users ON posts.user_id = users.id;

-- LEFT JOIN (include users without posts)
SELECT users.name, posts.title
FROM users
LEFT JOIN posts ON posts.user_id = users.id;
