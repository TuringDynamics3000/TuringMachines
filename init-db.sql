-- TuringMachines Database Initialization
-- Creates databases for each service

CREATE DATABASE turing_orchestrate;
CREATE DATABASE turingcapture;

-- Grant permissions
GRANT ALL PRIVILEGES ON DATABASE turing_orchestrate TO postgres;
GRANT ALL PRIVILEGES ON DATABASE turingcapture TO postgres;

-- Connect to turing_orchestrate and create pgvector extension
\c turing_orchestrate
CREATE EXTENSION IF NOT EXISTS vector;

-- Connect to turingcapture and create pgvector extension
\c turingcapture
CREATE EXTENSION IF NOT EXISTS vector;
