-- Script to set up dedicated read-only database user for SQL Agent

DO $$
BEGIN
   IF NOT EXISTS (SELECT FROM pg_catalog.pg_roles WHERE rolname = 'llm_readonly') THEN
      CREATE USER llm_readonly WITH PASSWORD 'readonly_secure_pass';
   END IF;
END $$;

GRANT CONNECT ON DATABASE electricity TO llm_readonly;
GRANT USAGE ON SCHEMA public TO llm_readonly;
GRANT SELECT ON ALL TABLES IN SCHEMA public TO llm_readonly;
ALTER DEFAULT PRIVILEGES IN SCHEMA public GRANT SELECT ON TABLES TO llm_readonly;

-- Revoke write and administrative privileges explicitly
REVOKE INSERT, UPDATE, DELETE, TRUNCATE, REFERENCES, TRIGGER ON ALL TABLES IN SCHEMA public FROM llm_readonly;
REVOKE CREATE ON SCHEMA public FROM llm_readonly;
