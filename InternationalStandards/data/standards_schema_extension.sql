-- Standards Integration Schema Extensions
-- Adds support for academic standards classification and dual storage

-- Add new columns to retrieved_documents table for standards support
DO $$ 
BEGIN
    -- Add standards classification fields
    IF NOT EXISTS (SELECT 1 FROM information_schema.columns 
                   WHERE table_name = 'retrieved_documents' AND column_name = 'standards_classification') THEN
        ALTER TABLE retrieved_documents ADD COLUMN standards_classification TEXT;
    END IF;
    
    IF NOT EXISTS (SELECT 1 FROM information_schema.columns 
                   WHERE table_name = 'retrieved_documents' AND column_name = 'repository_name') THEN
        ALTER TABLE retrieved_documents ADD COLUMN repository_name TEXT;
    END IF;
    
    IF NOT EXISTS (SELECT 1 FROM information_schema.columns 
                   WHERE table_name = 'retrieved_documents' AND column_name = 'education_level') THEN
        ALTER TABLE retrieved_documents ADD COLUMN education_level TEXT;
    END IF;
    
    IF NOT EXISTS (SELECT 1 FROM information_schema.columns 
                   WHERE table_name = 'retrieved_documents' AND column_name = 'language') THEN
        ALTER TABLE retrieved_documents ADD COLUMN language TEXT DEFAULT 'english';
    END IF;
    
    IF NOT EXISTS (SELECT 1 FROM information_schema.columns 
                   WHERE table_name = 'retrieved_documents' AND column_name = 'openbooks_subject') THEN
        ALTER TABLE retrieved_documents ADD COLUMN openbooks_subject TEXT;
    END IF;
    
    IF NOT EXISTS (SELECT 1 FROM information_schema.columns 
                   WHERE table_name = 'retrieved_documents' AND column_name = 'standards_path') THEN
        ALTER TABLE retrieved_documents ADD COLUMN standards_path TEXT;
    END IF;
    
    IF NOT EXISTS (SELECT 1 FROM information_schema.columns 
                   WHERE table_name = 'retrieved_documents' AND column_name = 'json_path') THEN
        ALTER TABLE retrieved_documents ADD COLUMN json_path TEXT;
    END IF;
END $$;

-- Add new columns to educational_standards table
DO $$ 
BEGIN
    IF NOT EXISTS (SELECT 1 FROM information_schema.columns 
                   WHERE table_name = 'educational_standards' AND column_name = 'json_extracted_path') THEN
        ALTER TABLE educational_standards ADD COLUMN json_extracted_path TEXT;
    END IF;
    
    IF NOT EXISTS (SELECT 1 FROM information_schema.columns 
                   WHERE table_name = 'educational_standards' AND column_name = 'original_document_path') THEN
        ALTER TABLE educational_standards ADD COLUMN original_document_path TEXT;
    END IF;
    
    IF NOT EXISTS (SELECT 1 FROM information_schema.columns 
                   WHERE table_name = 'educational_standards' AND column_name = 'repository_source') THEN
        ALTER TABLE educational_standards ADD COLUMN repository_source TEXT;
    END IF;
END $$;

-- Add new columns to standards_sources table
DO $$ 
BEGIN
    IF NOT EXISTS (SELECT 1 FROM information_schema.columns 
                   WHERE table_name = 'standards_sources' AND column_name = 'standards_focus') THEN
        ALTER TABLE standards_sources ADD COLUMN standards_focus TEXT;
    END IF;
    
    IF NOT EXISTS (SELECT 1 FROM information_schema.columns 
                   WHERE table_name = 'standards_sources' AND column_name = 'target_education_levels') THEN
        ALTER TABLE standards_sources ADD COLUMN target_education_levels TEXT;
    END IF;
END $$;

-- Create indexes for better query performance
CREATE INDEX IF NOT EXISTS idx_retrieved_documents_standards 
ON retrieved_documents(standards_classification, repository_name, education_level, language);

CREATE INDEX IF NOT EXISTS idx_retrieved_documents_openbooks_subject 
ON retrieved_documents(openbooks_subject);

CREATE INDEX IF NOT EXISTS idx_educational_standards_repository 
ON educational_standards(repository_source);

-- Create view for standards summary
CREATE OR REPLACE VIEW v_standards_summary AS
SELECT 
    d.discipline_name,
    d.display_name,
    rd.language,
    rd.openbooks_subject,
    rd.education_level,  
    rd.repository_name,
    rd.standards_classification,
    COUNT(*) as document_count,
    AVG(ss.quality_score) as avg_quality_score,
    MAX(rd.download_timestamp) as latest_update
FROM retrieved_documents rd
JOIN disciplines d ON rd.discipline_id = d.discipline_id
JOIN standards_sources ss ON rd.source_id = ss.source_id
WHERE rd.standards_classification IS NOT NULL
GROUP BY d.discipline_name, d.display_name, rd.language, rd.openbooks_subject, 
         rd.education_level, rd.repository_name, rd.standards_classification
ORDER BY d.discipline_name, rd.openbooks_subject, rd.education_level;

-- Create view for API-ready standards
CREATE OR REPLACE VIEW v_api_standards AS
SELECT 
    rd.document_id,
    rd.document_title,
    d.discipline_name,
    rd.openbooks_subject,
    rd.education_level,
    rd.repository_name,
    rd.standards_classification,
    rd.language,
    rd.json_path,
    rd.standards_path,
    rd.download_timestamp,
    ss.quality_score,
    ss.source_title
FROM retrieved_documents rd
JOIN disciplines d ON rd.discipline_id = d.discipline_id
JOIN standards_sources ss ON rd.source_id = ss.source_id
WHERE rd.standards_classification IS NOT NULL 
  AND rd.json_path IS NOT NULL
ORDER BY rd.download_timestamp DESC;

-- Insert sample education levels for reference
INSERT INTO system_config (config_key, config_value, description) VALUES
('education_levels', '["K-12", "HighSchool", "University", "Graduate"]', 'Supported education levels (OpenBooks compatible)')
ON CONFLICT (config_key) DO UPDATE SET 
config_value = EXCLUDED.config_value,
updated_at = CURRENT_TIMESTAMP;

-- Insert sample repository types
INSERT INTO system_config (config_key, config_value, description) VALUES
('repository_types', '{"curriculum": ["CommonCore", "NGSS", "CSTA_Standards", "State_Standards"], "accreditation": ["ABET", "AACSB", "LCME", "Regional_Accreditors"], "assessment": ["MCAT", "GRE", "AP_Exams", "IB_Standards", "Professional_Certs"]}', 'Academic standards repository types')
ON CONFLICT (config_key) DO UPDATE SET 
config_value = EXCLUDED.config_value,
updated_at = CURRENT_TIMESTAMP;

-- Insert OpenBooks subject mappings  
INSERT INTO system_config (config_key, config_value, description) VALUES
('openbooks_subject_mapping', '{"Computer_Science": "Computer science", "Physical_Sciences": "Physics", "Life_Sciences": "Biology", "Health_Sciences": "Medicine", "Mathematics": "Mathematics", "Engineering": "Engineering", "Economics": "Economics", "Business": "Business", "Education": "Education", "Social_Sciences": "Sociology", "Art": "Art", "History": "History", "Philosophy": "Philosophy", "Law": "Law", "Literature": "Literature", "Geography": "Geography", "Environmental_Science": "Environmental Science", "Earth_Sciences": "Earth Sciences", "Agricultural_Sciences": "Agriculture"}', 'OpenAlex to OpenBooks subject mapping')
ON CONFLICT (config_key) DO UPDATE SET 
config_value = EXCLUDED.config_value,
updated_at = CURRENT_TIMESTAMP;

COMMIT;