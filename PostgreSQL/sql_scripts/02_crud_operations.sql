-- =========================================================
-- 02 - CRUD OPERATIONS
-- Problem:
-- We need to Create, Read, Update, Delete data.
-- =========================================================

-- INSERT (Create)
INSERT INTO users (name, email, age)
VALUES ('Abdullah', 'abdullah@example.com', 25);

-- SELECT (Read)
SELECT * FROM users;

-- WHERE filtering
SELECT * FROM users
WHERE age > 20;

-- ORDER BY
SELECT * FROM users
ORDER BY age DESC;

-- LIMIT (Pagination)
SELECT * FROM users
LIMIT 5 OFFSET 0;

-- UPDATE
UPDATE users
SET age = 26
WHERE email = 'abdullah@example.com';

-- DELETE
DELETE FROM users
WHERE age < 18;
