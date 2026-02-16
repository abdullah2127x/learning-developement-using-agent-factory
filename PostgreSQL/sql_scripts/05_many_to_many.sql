-- =========================================================
-- 05 - MANY TO MANY RELATIONSHIP
-- Problem:
-- Students can take many courses.
-- Courses can have many students.
-- Solution: Bridge table.
-- =========================================================

CREATE TABLE students (
    id SERIAL PRIMARY KEY,
    name TEXT NOT NULL
);

CREATE TABLE courses (
    id SERIAL PRIMARY KEY,
    title TEXT NOT NULL
);

-- Bridge table
CREATE TABLE enrollments (
    student_id INT REFERENCES students(id),
    course_id INT REFERENCES courses(id),
    PRIMARY KEY (student_id, course_id)
);

-- Example query: courses of a student
SELECT courses.title
FROM enrollments
JOIN courses ON enrollments.course_id = courses.id
WHERE enrollments.student_id = 1;
