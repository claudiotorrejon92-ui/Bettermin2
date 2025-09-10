-- DuckDB migration: create measurements table
CREATE TABLE IF NOT EXISTS measurements (
    name VARCHAR,
    value DOUBLE,
    unit VARCHAR,
    mean DOUBLE,
    std DOUBLE
);
