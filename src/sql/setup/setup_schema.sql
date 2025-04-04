-- Create extension for UUID generation
CREATE EXTENSION IF NOT EXISTS "pgcrypto";

-- Create ID generation function
CREATE OR REPLACE FUNCTION generate_short_id(prefix text)
RETURNS text AS $$
DECLARE
  id_value text;
  check_count integer;
BEGIN
  LOOP
    id_value := prefix || substring(encode(gen_random_bytes(5), 'hex') from 1 for 7);
    check_count := 0;
    IF check_count = 0 THEN
      RETURN id_value;
    END IF;
  END LOOP;
END;
$$ LANGUAGE plpgsql;

-- Create reference schema
CREATE SCHEMA IF NOT EXISTS ref;