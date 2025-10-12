-- Migration: Add session_id and metadata fields to customers table
-- Execute this in your Supabase SQL Editor if you have an existing database

-- Add session_id column
ALTER TABLE customers 
ADD COLUMN IF NOT EXISTS session_id VARCHAR(255);

-- Add metadata column with default empty JSON array
ALTER TABLE customers 
ADD COLUMN IF NOT EXISTS metadata JSONB DEFAULT '[]'::jsonb;

-- Update existing customers to have empty metadata array
UPDATE customers 
SET metadata = '[]'::jsonb 
WHERE metadata IS NULL;

-- Verify the changes
SELECT 
    column_name, 
    data_type, 
    column_default 
FROM information_schema.columns 
WHERE table_name = 'customers' 
AND column_name IN ('session_id', 'metadata');

