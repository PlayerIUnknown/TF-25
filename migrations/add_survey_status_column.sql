-- Migration: Add survey_status column to customers table
-- Date: 2025-10-12
-- Description: Adds a survey_status column to track completion state of customer surveys

-- Add survey_status column to customers table
ALTER TABLE customers 
ADD COLUMN IF NOT EXISTS survey_status VARCHAR(50) DEFAULT 'in_progress';

-- Update existing records to set status based on metadata
-- If metadata has 6 entries (all blocks), set to 'completed', otherwise 'in_progress'
UPDATE customers
SET survey_status = CASE 
    WHEN jsonb_array_length(metadata) >= 6 THEN 'completed'
    ELSE 'in_progress'
END
WHERE survey_status IS NULL OR survey_status = 'in_progress';

-- Create index for faster queries on survey_status
CREATE INDEX IF NOT EXISTS idx_customers_survey_status ON customers(survey_status);

-- Comment on column
COMMENT ON COLUMN customers.survey_status IS 'Status of survey completion: in_progress, completed';

