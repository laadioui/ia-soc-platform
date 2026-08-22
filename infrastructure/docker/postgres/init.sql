-- AI SOC Platform - PostgreSQL Initialization
-- This script runs on first container start

-- Enable extensions
CREATE EXTENSION IF NOT EXISTS "uuid-ossp";
CREATE EXTENSION IF NOT EXISTS "pgcrypto";
CREATE EXTENSION IF NOT EXISTS "pg_trgm";

-- Create custom types
DO $$ BEGIN
    CREATE TYPE user_role AS ENUM ('admin', 'manager', 'analyst', 'viewer');
EXCEPTION WHEN duplicate_object THEN null; END $$;

DO $$ BEGIN
    CREATE TYPE incident_status AS ENUM ('new', 'investigating', 'contained', 'resolved', 'false_positive', 'closed');
EXCEPTION WHEN duplicate_object THEN null; END $$;

DO $$ BEGIN
    CREATE TYPE severity_level AS ENUM ('info', 'low', 'medium', 'high', 'critical');
EXCEPTION WHEN duplicate_object THEN null; END $$;

DO $$ BEGIN
    CREATE TYPE risk_level AS ENUM ('low', 'medium', 'high', 'critical');
EXCEPTION WHEN duplicate_object THEN null; END $$;

DO $$ BEGIN
    CREATE TYPE alert_status AS ENUM ('new', 'acknowledged', 'investigating', 'resolved', 'false_positive');
EXCEPTION WHEN duplicate_object THEN null; END $$;

-- Create indexes for full-text search
-- (Additional indexes are created by Alembic migrations)
