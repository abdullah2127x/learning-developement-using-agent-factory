-- =========================================================
-- 06 - INDEXES
-- Problem:
-- Searching large tables becomes slow.
-- Index speeds up lookups.
-- =========================================================

-- Create index on age column
CREATE INDEX idx_users_age ON users(age);

-- Primary keys and UNIQUE columns are indexed automatically.
