-- Create core tables for the knowledge repository

-- Reference tables for attributes that can have multiple values
CREATE TABLE IF NOT EXISTS ref.person_types (
    id SERIAL PRIMARY KEY,
    name TEXT UNIQUE NOT NULL
);

CREATE TABLE IF NOT EXISTS ref.nationalities (
    id SERIAL PRIMARY KEY,
    name TEXT UNIQUE NOT NULL
);

-- People table (for thinkers, artists, authors, etc)
CREATE TABLE IF NOT EXISTS people (
    id TEXT PRIMARY KEY DEFAULT generate_short_id('p'),
    name TEXT NOT NULL,
    surname TEXT,
    real_name TEXT,
    gender TEXT,
    complete_name_ns TEXT GENERATED ALWAYS AS (COALESCE(name, '') || ', ' || COALESCE(surname, '')) STORED,
    complete_name_sn TEXT GENERATED ALWAYS AS (COALESCE(surname, '') || ', ' || COALESCE(name, '')) STORED,
    has_image BOOLEAN DEFAULT FALSE,
    created_at TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP
);

-- Junction tables for many-to-many relationships
CREATE TABLE IF NOT EXISTS person_types_junction (
    person_id TEXT REFERENCES people(id),
    type_id INTEGER REFERENCES ref.person_types(id),
    PRIMARY KEY (person_id, type_id)
);

CREATE TABLE IF NOT EXISTS person_nationalities_junction (
    person_id TEXT REFERENCES people(id),
    nationality_id INTEGER REFERENCES ref.nationalities(id),
    PRIMARY KEY (person_id, nationality_id)
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