-- =========================================================
-- 01 - BASIC TABLE CREATION
-- What problem does this solve?
-- We need structured storage for data.
-- Tables store rows and columns with types.
-- =========================================================

-- Create users table
CREATE TABLE users (
    id SERIAL PRIMARY KEY,         -- Auto increment unique ID
    name TEXT NOT NULL,            -- Required string
    email TEXT UNIQUE NOT NULL,    -- Must be unique
    age INT,                       -- Integer column
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

-- View tables
SELECT table_name 
FROM information_schema.tables
WHERE table_schema = 'public';
