-- Create the database if it doesn't exist
DO $$ 
BEGIN
    IF NOT EXISTS (SELECT FROM pg_database WHERE datname = 'phantom_db') THEN
        CREATE DATABASE phantom_db;
    END IF;
END
$$;