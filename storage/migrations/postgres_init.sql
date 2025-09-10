-- PostgreSQL migration: create measurements table
CREATE TABLE IF NOT EXISTS measurements (
    id SERIAL PRIMARY KEY,
    name TEXT,
    value DOUBLE PRECISION,
    unit TEXT,
    mean DOUBLE PRECISION,
    std DOUBLE PRECISION
);
