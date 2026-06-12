-- Prompt Teacher Database Initialization
-- This script runs when the PostgreSQL container is first created

-- Grant privileges
GRANT ALL PRIVILEGES ON DATABASE prompt_teaching_db TO postgres;

-- Create extensions if needed
CREATE EXTENSION IF NOT EXISTS "uuid-ossp";
CREATE EXTENSION IF NOT EXISTS "pg_trgm";
