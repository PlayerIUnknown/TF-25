-- AI-Enabled Survey Service Database Schema
-- Execute this in your Supabase SQL Editor

-- Enable UUID extension
CREATE EXTENSION IF NOT EXISTS "uuid-ossp";

-- Companies Table
-- Note: UUIDs are provided by the React frontend
CREATE TABLE IF NOT EXISTS companies (
    uuid UUID PRIMARY KEY,
    name VARCHAR(255) NOT NULL,
    sector VARCHAR(100),
    products TEXT,
    details TEXT,
    created_at TIMESTAMP WITH TIME ZONE DEFAULT NOW(),
    updated_at TIMESTAMP WITH TIME ZONE DEFAULT NOW()
);

-- Surveys Table
-- Note: UUIDs are provided by the React frontend
CREATE TABLE IF NOT EXISTS surveys (
    uuid UUID PRIMARY KEY,
    company_uuid UUID NOT NULL REFERENCES companies(uuid) ON DELETE CASCADE,
    title VARCHAR(255) NOT NULL,
    description TEXT,
    status VARCHAR(50) DEFAULT 'active',
    created_at TIMESTAMP WITH TIME ZONE DEFAULT NOW(),
    updated_at TIMESTAMP WITH TIME ZONE DEFAULT NOW()
);

-- Customers Table (Survey Respondents)
-- Note: UUIDs are provided by the React frontend
CREATE TABLE IF NOT EXISTS customers (
    uuid UUID PRIMARY KEY,
    survey_uuid UUID NOT NULL REFERENCES surveys(uuid) ON DELETE CASCADE,
    name VARCHAR(255) NOT NULL,
    age INTEGER NOT NULL,
    gender VARCHAR(50) NOT NULL,
    session_id VARCHAR(255),
    metadata JSONB DEFAULT '[]'::jsonb,
    survey_status VARCHAR(50) DEFAULT 'in_progress',
    created_at TIMESTAMP WITH TIME ZONE DEFAULT NOW()
);

-- Chat Messages Table
-- Note: Message UUIDs can be auto-generated as they're internal
CREATE TABLE IF NOT EXISTS chat_messages (
    uuid UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    customer_uuid UUID NOT NULL REFERENCES customers(uuid) ON DELETE CASCADE,
    survey_uuid UUID NOT NULL REFERENCES surveys(uuid) ON DELETE CASCADE,
    message TEXT NOT NULL,
    sender VARCHAR(50) NOT NULL CHECK (sender IN ('user', 'ai')),
    created_at TIMESTAMP WITH TIME ZONE DEFAULT NOW()
);

-- Create indexes for better query performance
CREATE INDEX IF NOT EXISTS idx_surveys_company ON surveys(company_uuid);
CREATE INDEX IF NOT EXISTS idx_customers_survey ON customers(survey_uuid);
CREATE INDEX IF NOT EXISTS idx_chat_messages_customer ON chat_messages(customer_uuid);
CREATE INDEX IF NOT EXISTS idx_chat_messages_survey ON chat_messages(survey_uuid);
CREATE INDEX IF NOT EXISTS idx_chat_messages_created_at ON chat_messages(created_at);

-- Create updated_at trigger function
CREATE OR REPLACE FUNCTION update_updated_at_column()
RETURNS TRIGGER AS $$
BEGIN
    NEW.updated_at = NOW();
    RETURN NEW;
END;
$$ language 'plpgsql';

-- Add triggers for updated_at
DROP TRIGGER IF EXISTS update_companies_updated_at ON companies;
CREATE TRIGGER update_companies_updated_at
    BEFORE UPDATE ON companies
    FOR EACH ROW
    EXECUTE FUNCTION update_updated_at_column();

DROP TRIGGER IF EXISTS update_surveys_updated_at ON surveys;
CREATE TRIGGER update_surveys_updated_at
    BEFORE UPDATE ON surveys
    FOR EACH ROW
    EXECUTE FUNCTION update_updated_at_column();

-- Enable Row Level Security (Optional - uncomment if needed)
-- ALTER TABLE companies ENABLE ROW LEVEL SECURITY;
-- ALTER TABLE surveys ENABLE ROW LEVEL SECURITY;
-- ALTER TABLE customers ENABLE ROW LEVEL SECURITY;
-- ALTER TABLE chat_messages ENABLE ROW LEVEL SECURITY;

-- Create policies (Optional - uncomment and customize as needed)
-- CREATE POLICY "Enable read access for all users" ON companies FOR SELECT USING (true);
-- CREATE POLICY "Enable insert for all users" ON companies FOR INSERT WITH CHECK (true);

