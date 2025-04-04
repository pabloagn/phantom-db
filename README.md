# Phantom-DB
My knowledge repository.

## Info

- [GitHub Repository](https://github.com/pabloagn/phantom-db)
- [Contact](mailto:main@phantomklange.com)

## Environment Setup

Clone or pull the repository.

To create a virtual environment in Python using WSL with Ubuntu, you can use this command:

```bash
python3 -m venv .venv
```

Activate it:

```bash
source .venv/bin/activate
```

Install requirements:

```bash
pip install -r requirements.txt
```

## Initial Config

Install PostgreSQL in WSL2:

```bash
sudo apt update
sudo apt install postgresql postgresql-contrib
```

Start PostgreSQL service:

```bash
sudo service postgresql start
```

Create two database users:

1. Development environment
2. Production
3. Reader

- For the development environment:

```bash
sudo -u postgres createuser --interactive --pwprompt
```

- For the production environment:

```bash
sudo -u postgres createuser --no-superuser --createdb --pwprompt knowledgerepo_user
```

- For the reader:

```bash
sudo -u postgres createuser --no-superuser --createdb --pwprompt knowledgerepo_user
```

Create database:

```bash
sudo -u postgres psql -c "CREATE DATABASE phantom_db OWNER phantom_admin;"
```

Connect to database with username and password:

```bash
psql -U phantom_admin -d phantom_db
```

To connect using VS Code, simply use PostgreSQL VS Code extension.

## Setup

Run the following from WSL2 in the same order:

Command:

```bash
psql -h localhost -U phantom_admin -d phantom_db -f setup_schema.sql
```

Script:

```SQL
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
```

Command:

```bash
psql -h localhost -U phantom_admin -d phantom_db -f create_core_tables.sql
```

Script:

```SQL
-- Create core tables for the knowledge repository

-- People table (for thinkers, artists, authors, etc)
CREATE TABLE IF NOT EXISTS people (
    id TEXT PRIMARY KEY DEFAULT generate_short_id('p'),
    name TEXT NOT NULL,
    surname TEXT,
    real_name TEXT,
    type TEXT,
    gender TEXT,
    nationality TEXT,
    complete_name_ns TEXT GENERATED ALWAYS AS (COALESCE(name, '') || ', ' || COALESCE(surname, '')) STORED,
    complete_name_sn TEXT GENERATED ALWAYS AS (COALESCE(surname, '') || ', ' || COALESCE(name, '')) STORED,
    has_image BOOLEAN DEFAULT FALSE,
    created_at TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP
);

-- Work Types reference table
CREATE TABLE IF NOT EXISTS ref.work_types (
    id SERIAL PRIMARY KEY,
    name TEXT UNIQUE NOT NULL
);

-- Create base Works table
CREATE TABLE IF NOT EXISTS works (
    id TEXT PRIMARY KEY,
    title TEXT NOT NULL,
    type_id INTEGER REFERENCES ref.work_types(id),
    created_at TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP
);

-- Books table
CREATE TABLE IF NOT EXISTS books (
    id TEXT PRIMARY KEY,
    work_id TEXT REFERENCES works(id),
    author TEXT NOT NULL,
    composite_work_author TEXT,
    composite_author_work TEXT,
    published_date INTEGER,
    page_count INTEGER,
    description TEXT,
    rating NUMERIC(3,2),
    read BOOLEAN DEFAULT FALSE,
    cover_raw BOOLEAN DEFAULT FALSE,
    cover_ftd BOOLEAN DEFAULT FALSE,
    published_date_decade TEXT,
    published_date_century TEXT
);

-- Book Editions table
CREATE TABLE IF NOT EXISTS book_editions (
    id SERIAL PRIMARY KEY,
    book_id TEXT REFERENCES books(id),
    edition TEXT,
    publisher TEXT,
    published_title TEXT,
    published_language TEXT,
    published_date INTEGER,
    isbn TEXT,
    created_at TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP
);

-- Paintings table
CREATE TABLE IF NOT EXISTS paintings (
    id TEXT PRIMARY KEY DEFAULT generate_short_id('p'),
    work_id TEXT REFERENCES works(id),
    author TEXT NOT NULL,
    composite TEXT,
    art_movement TEXT,
    orientation TEXT,
    century TEXT
);

-- Films table
CREATE TABLE IF NOT EXISTS films (
    id TEXT PRIMARY KEY DEFAULT generate_short_id('f'),
    work_id TEXT REFERENCES works(id),
    director TEXT NOT NULL,
    composite_work_author TEXT,
    composite_author_work TEXT,
    year INTEGER,
    decade TEXT,
    century TEXT
);

-- Insert common work types
INSERT INTO ref.work_types (name) 
VALUES ('Book'), ('Film'), ('Painting'), ('Photograph'), ('Perfume')
ON CONFLICT (name) DO NOTHING;

-- Create indexes for performance
CREATE INDEX IF NOT EXISTS idx_books_author ON books(author);
CREATE INDEX IF NOT EXISTS idx_paintings_author ON paintings(author);
CREATE INDEX IF NOT EXISTS idx_films_director ON films(director);
CREATE INDEX IF NOT EXISTS idx_people_name ON people(name);
CREATE INDEX IF NOT EXISTS idx_people_surname ON people(surname);
```

## Import

Now we import our data into the tables.