-- International Standards Retrieval System Database Schema
-- Programmatic data storage organized by 19 OpenAlex disciplines
-- Author: Autonomous AI Development System

-- ==============================================================================
-- CORE DISCIPLINE TAXONOMY TABLES
-- ==============================================================================

-- Primary disciplines table based on OpenAlex taxonomy
CREATE TABLE disciplines (
    discipline_id SERIAL PRIMARY KEY,
    openalex_id VARCHAR(50) UNIQUE NOT NULL,
    discipline_name VARCHAR(100) NOT NULL,
    display_name VARCHAR(150) NOT NULL,
    description TEXT,
    priority_level INTEGER DEFAULT 5,
    parent_discipline_id INTEGER REFERENCES disciplines(discipline_id),
    is_active BOOLEAN DEFAULT TRUE,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

-- Subdisciplines within each major discipline
CREATE TABLE subdisciplines (
    subdiscipline_id SERIAL PRIMARY KEY,
    discipline_id INTEGER NOT NULL REFERENCES disciplines(discipline_id),
    subdiscipline_name VARCHAR(100) NOT NULL,
    openalex_concept_id VARCHAR(50),
    description TEXT,
    weight DECIMAL(3,2) DEFAULT 1.00,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    UNIQUE(discipline_id, subdiscipline_name)
);

-- ==============================================================================
-- STANDARDS DISCOVERY AND SOURCE MANAGEMENT
-- ==============================================================================

-- Standards sources discovered by discovery agents
CREATE TABLE standards_sources (
    source_id SERIAL PRIMARY KEY,
    discipline_id INTEGER NOT NULL REFERENCES disciplines(discipline_id),
    source_url TEXT NOT NULL,
    source_title VARCHAR(500),
    source_type VARCHAR(50), -- 'government', 'professional_org', 'academic', etc.
    authority_score DECIMAL(4,3) DEFAULT 0.000,
    quality_score DECIMAL(4,3) DEFAULT 0.000,
    relevance_score DECIMAL(4,3) DEFAULT 0.000,
    discovery_method VARCHAR(50), -- 'web_search', 'api_discovery', 'manual'
    discovery_timestamp TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    last_validated TIMESTAMP,
    validation_status VARCHAR(20) DEFAULT 'pending', -- 'pending', 'validated', 'failed'
    is_active BOOLEAN DEFAULT TRUE,
    metadata JSONB,
    UNIQUE(source_url, discipline_id)
);

-- Documents retrieved from standards sources
CREATE TABLE retrieved_documents (
    document_id SERIAL PRIMARY KEY,
    source_id INTEGER NOT NULL REFERENCES standards_sources(source_id),
    discipline_id INTEGER NOT NULL REFERENCES disciplines(discipline_id),
    document_url TEXT NOT NULL,
    document_title VARCHAR(500),
    document_type VARCHAR(50), -- 'pdf', 'html', 'doc', 'txt'
    file_path TEXT,
    file_size BIGINT,
    content_hash VARCHAR(64), -- SHA256 hash for deduplication
    download_timestamp TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    processing_status VARCHAR(20) DEFAULT 'pending', -- 'pending', 'processed', 'failed'
    content_extracted BOOLEAN DEFAULT FALSE,
    extraction_method VARCHAR(50),
    metadata JSONB,
    UNIQUE(content_hash)
);

-- ==============================================================================
-- STANDARDS EXTRACTION AND CLASSIFICATION
-- ==============================================================================

-- Extracted educational standards
CREATE TABLE educational_standards (
    standard_id SERIAL PRIMARY KEY,
    document_id INTEGER NOT NULL REFERENCES retrieved_documents(document_id),
    discipline_id INTEGER NOT NULL REFERENCES disciplines(discipline_id),
    subdiscipline_id INTEGER REFERENCES subdisciplines(subdiscipline_id),
    standard_text TEXT NOT NULL,
    standard_type VARCHAR(50), -- 'learning_objective', 'competency', 'assessment_criterion'
    education_level VARCHAR(50), -- 'K-12', 'undergraduate', 'graduate', 'professional'
    cognitive_level VARCHAR(50), -- Bloom's taxonomy: 'remember', 'understand', 'apply', etc.
    confidence_score DECIMAL(4,3) DEFAULT 0.000,
    extraction_method VARCHAR(50), -- 'pattern_matching', 'llm_extraction', 'manual'
    position_in_document INTEGER,
    context_snippet TEXT,
    processed_timestamp TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    validation_score DECIMAL(4,3),
    is_validated BOOLEAN DEFAULT FALSE,
    metadata JSONB
);

-- Competency mappings extracted from standards
CREATE TABLE competency_mappings (
    competency_id SERIAL PRIMARY KEY,
    standard_id INTEGER NOT NULL REFERENCES educational_standards(standard_id),
    discipline_id INTEGER NOT NULL REFERENCES disciplines(discipline_id),
    competency_statement TEXT NOT NULL,
    competency_category VARCHAR(50), -- 'knowledge', 'skill', 'attitude'
    bloom_level VARCHAR(20), -- 'remembering', 'understanding', 'applying', etc.
    subject_area VARCHAR(100),
    target_audience VARCHAR(100),
    assessment_methods TEXT[],
    prerequisite_competencies INTEGER[],
    learning_outcomes TEXT[],
    difficulty_level INTEGER DEFAULT 1, -- 1-5 scale
    estimated_hours DECIMAL(5,2),
    created_timestamp TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    metadata JSONB
);

-- ==============================================================================
-- QUALITY ASSURANCE AND VALIDATION
-- ==============================================================================

-- Validation results for standards and documents
CREATE TABLE validation_results (
    validation_id SERIAL PRIMARY KEY,
    target_type VARCHAR(20) NOT NULL, -- 'document', 'standard', 'competency'
    target_id INTEGER NOT NULL, -- ID of the validated item
    discipline_id INTEGER NOT NULL REFERENCES disciplines(discipline_id),
    validator_agent_id VARCHAR(100),
    accuracy_score DECIMAL(4,3) DEFAULT 0.000,
    completeness_score DECIMAL(4,3) DEFAULT 0.000,
    relevance_score DECIMAL(4,3) DEFAULT 0.000,
    consistency_score DECIMAL(4,3) DEFAULT 0.000,
    authority_score DECIMAL(4,3) DEFAULT 0.000,
    overall_quality_score DECIMAL(4,3) DEFAULT 0.000,
    quality_threshold_met BOOLEAN DEFAULT FALSE,
    validation_method VARCHAR(50),
    validation_timestamp TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    recommendations TEXT[],
    issues_identified TEXT[],
    validation_details JSONB
);

-- Quality metrics aggregated by discipline
CREATE TABLE discipline_quality_metrics (
    metric_id SERIAL PRIMARY KEY,
    discipline_id INTEGER NOT NULL REFERENCES disciplines(discipline_id),
    measurement_date DATE DEFAULT CURRENT_DATE,
    total_standards INTEGER DEFAULT 0,
    validated_standards INTEGER DEFAULT 0,
    avg_quality_score DECIMAL(5,3) DEFAULT 0.000,
    avg_accuracy_score DECIMAL(5,3) DEFAULT 0.000,
    avg_completeness_score DECIMAL(5,3) DEFAULT 0.000,
    threshold_compliance_rate DECIMAL(5,3) DEFAULT 0.000,
    processing_efficiency DECIMAL(5,3) DEFAULT 0.000,
    data_freshness_score DECIMAL(5,3) DEFAULT 0.000,
    coverage_completeness DECIMAL(5,3) DEFAULT 0.000,
    metadata JSONB,
    UNIQUE(discipline_id, measurement_date)
);

-- ==============================================================================
-- SYSTEM PROCESSING AND AGENT TRACKING
-- ==============================================================================

-- Agent processing sessions and performance
CREATE TABLE agent_sessions (
    session_id SERIAL PRIMARY KEY,
    agent_id VARCHAR(100) NOT NULL,
    agent_type VARCHAR(50) NOT NULL, -- 'discovery', 'retrieval', 'processing', 'validation'
    discipline_id INTEGER REFERENCES disciplines(discipline_id),
    session_start TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    session_end TIMESTAMP,
    tasks_completed INTEGER DEFAULT 0,
    tasks_failed INTEGER DEFAULT 0,
    success_rate DECIMAL(5,3) DEFAULT 0.000,
    processing_time_seconds INTEGER DEFAULT 0,
    tokens_used INTEGER DEFAULT 0,
    llm_cost DECIMAL(10,4) DEFAULT 0.0000,
    performance_score DECIMAL(4,3) DEFAULT 0.000,
    status VARCHAR(20) DEFAULT 'active', -- 'active', 'completed', 'failed', 'terminated'
    error_logs TEXT[],
    metadata JSONB
);

-- Task execution tracking
CREATE TABLE task_executions (
    task_id SERIAL PRIMARY KEY,
    session_id INTEGER NOT NULL REFERENCES agent_sessions(session_id),
    task_type VARCHAR(50) NOT NULL,
    discipline_id INTEGER REFERENCES disciplines(discipline_id),
    task_parameters JSONB,
    start_timestamp TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    end_timestamp TIMESTAMP,
    execution_status VARCHAR(20) DEFAULT 'pending', -- 'pending', 'running', 'completed', 'failed'
    result_data JSONB,
    tokens_consumed INTEGER DEFAULT 0,
    llm_cost DECIMAL(8,4) DEFAULT 0.0000,
    processing_time_ms INTEGER DEFAULT 0,
    quality_score DECIMAL(4,3),
    error_message TEXT,
    retry_count INTEGER DEFAULT 0
);

-- ==============================================================================
-- LLM USAGE AND OPTIMIZATION TRACKING
-- ==============================================================================

-- LLM model usage statistics
CREATE TABLE llm_usage_stats (
    usage_id SERIAL PRIMARY KEY,
    discipline_id INTEGER REFERENCES disciplines(discipline_id),
    model_name VARCHAR(100) NOT NULL,
    task_type VARCHAR(50) NOT NULL,
    usage_timestamp TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    input_tokens INTEGER DEFAULT 0,
    output_tokens INTEGER DEFAULT 0,
    total_tokens INTEGER DEFAULT 0,
    cost_usd DECIMAL(10,6) DEFAULT 0.000000,
    response_time_ms INTEGER DEFAULT 0,
    quality_score DECIMAL(4,3),
    optimization_applied VARCHAR(100),
    cost_efficiency_ratio DECIMAL(8,4) DEFAULT 0.0000,
    session_id INTEGER REFERENCES agent_sessions(session_id)
);

-- Model performance optimization data
CREATE TABLE model_performance (
    performance_id SERIAL PRIMARY KEY,
    model_name VARCHAR(100) NOT NULL,
    discipline_id INTEGER REFERENCES disciplines(discipline_id),
    task_type VARCHAR(50) NOT NULL,
    evaluation_date DATE DEFAULT CURRENT_DATE,
    avg_quality_score DECIMAL(5,3) DEFAULT 0.000,
    avg_response_time_ms INTEGER DEFAULT 0,
    avg_cost_per_request DECIMAL(8,6) DEFAULT 0.000000,
    success_rate DECIMAL(5,3) DEFAULT 0.000,
    total_requests INTEGER DEFAULT 0,
    cost_efficiency_rank INTEGER,
    quality_rank INTEGER,
    speed_rank INTEGER,
    overall_rank INTEGER,
    optimization_recommendations TEXT[],
    UNIQUE(model_name, discipline_id, task_type, evaluation_date)
);

-- ==============================================================================
-- SYSTEM RECOVERY AND VERSIONING
-- ==============================================================================

-- System checkpoints for recovery
CREATE TABLE system_checkpoints (
    checkpoint_id SERIAL PRIMARY KEY,
    checkpoint_name VARCHAR(200) NOT NULL,
    checkpoint_type VARCHAR(50) DEFAULT 'manual', -- 'manual', 'automatic', 'scheduled'
    created_timestamp TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    system_state JSONB NOT NULL,
    agent_states JSONB,
    processing_progress JSONB,
    data_integrity_hash VARCHAR(64),
    checkpoint_size_bytes BIGINT,
    restoration_tested BOOLEAN DEFAULT FALSE,
    retention_until TIMESTAMP,
    metadata JSONB
);

-- Data version control and change tracking
CREATE TABLE data_versions (
    version_id SERIAL PRIMARY KEY,
    table_name VARCHAR(100) NOT NULL,
    record_id INTEGER NOT NULL,
    discipline_id INTEGER REFERENCES disciplines(discipline_id),
    change_type VARCHAR(20) NOT NULL, -- 'insert', 'update', 'delete'
    changed_fields JSONB,
    old_values JSONB,
    new_values JSONB,
    change_timestamp TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    changed_by VARCHAR(100), -- agent_id or user_id
    change_reason VARCHAR(200),
    version_hash VARCHAR(64),
    is_active_version BOOLEAN DEFAULT TRUE
);

-- ==============================================================================
-- PROGRAMMATIC ACCESS AND API MANAGEMENT
-- ==============================================================================

-- API endpoints generated for external access
CREATE TABLE api_endpoints (
    endpoint_id SERIAL PRIMARY KEY,
    endpoint_path VARCHAR(200) NOT NULL UNIQUE,
    http_method VARCHAR(10) NOT NULL DEFAULT 'GET',
    discipline_filter INTEGER[] DEFAULT '{}', -- Array of discipline_ids
    description TEXT,
    query_template TEXT,
    response_format VARCHAR(20) DEFAULT 'json', -- 'json', 'xml', 'csv'
    access_level VARCHAR(20) DEFAULT 'public', -- 'public', 'authenticated', 'restricted'
    rate_limit_per_hour INTEGER DEFAULT 1000,
    cache_duration_seconds INTEGER DEFAULT 3600,
    created_timestamp TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    last_accessed TIMESTAMP,
    access_count INTEGER DEFAULT 0,
    is_active BOOLEAN DEFAULT TRUE,
    metadata JSONB
);

-- API access logs for monitoring
CREATE TABLE api_access_logs (
    log_id SERIAL PRIMARY KEY,
    endpoint_id INTEGER NOT NULL REFERENCES api_endpoints(endpoint_id),
    access_timestamp TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    client_ip INET,
    user_agent TEXT,
    discipline_requested INTEGER REFERENCES disciplines(discipline_id),
    query_parameters JSONB,
    response_status INTEGER,
    response_time_ms INTEGER,
    records_returned INTEGER DEFAULT 0,
    cache_hit BOOLEAN DEFAULT FALSE,
    api_key_used VARCHAR(100),
    error_message TEXT
);

-- ==============================================================================
-- INDEXES FOR OPTIMAL PERFORMANCE
-- ==============================================================================

-- Primary performance indexes
CREATE INDEX idx_disciplines_openalex ON disciplines(openalex_id);
CREATE INDEX idx_disciplines_active ON disciplines(is_active, priority_level);

CREATE INDEX idx_sources_discipline ON standards_sources(discipline_id);
CREATE INDEX idx_sources_quality ON standards_sources(quality_score DESC);
CREATE INDEX idx_sources_discovery_date ON standards_sources(discovery_timestamp DESC);

CREATE INDEX idx_documents_source ON retrieved_documents(source_id);
CREATE INDEX idx_documents_discipline ON retrieved_documents(discipline_id);
CREATE INDEX idx_documents_hash ON retrieved_documents(content_hash);
CREATE INDEX idx_documents_status ON retrieved_documents(processing_status);

CREATE INDEX idx_standards_discipline ON educational_standards(discipline_id);
CREATE INDEX idx_standards_document ON educational_standards(document_id);
CREATE INDEX idx_standards_type ON educational_standards(standard_type);
CREATE INDEX idx_standards_level ON educational_standards(education_level);
CREATE INDEX idx_standards_validated ON educational_standards(is_validated);
CREATE INDEX idx_standards_quality ON educational_standards(validation_score DESC);

CREATE INDEX idx_competencies_standard ON competency_mappings(standard_id);
CREATE INDEX idx_competencies_discipline ON competency_mappings(discipline_id);
CREATE INDEX idx_competencies_category ON competency_mappings(competency_category);

CREATE INDEX idx_validation_target ON validation_results(target_type, target_id);
CREATE INDEX idx_validation_discipline ON validation_results(discipline_id);
CREATE INDEX idx_validation_quality ON validation_results(overall_quality_score DESC);
CREATE INDEX idx_validation_timestamp ON validation_results(validation_timestamp DESC);

CREATE INDEX idx_agent_sessions_type ON agent_sessions(agent_type);
CREATE INDEX idx_agent_sessions_discipline ON agent_sessions(discipline_id);
CREATE INDEX idx_agent_sessions_status ON agent_sessions(status);

CREATE INDEX idx_task_executions_session ON task_executions(session_id);
CREATE INDEX idx_task_executions_type ON task_executions(task_type);
CREATE INDEX idx_task_executions_status ON task_executions(execution_status);

CREATE INDEX idx_llm_usage_discipline ON llm_usage_stats(discipline_id);
CREATE INDEX idx_llm_usage_model ON llm_usage_stats(model_name);
CREATE INDEX idx_llm_usage_timestamp ON llm_usage_stats(usage_timestamp DESC);

CREATE INDEX idx_checkpoints_timestamp ON system_checkpoints(created_timestamp DESC);
CREATE INDEX idx_checkpoints_type ON system_checkpoints(checkpoint_type);

CREATE INDEX idx_versions_table_record ON data_versions(table_name, record_id);
CREATE INDEX idx_versions_discipline ON data_versions(discipline_id);
CREATE INDEX idx_versions_active ON data_versions(is_active_version);

CREATE INDEX idx_api_endpoints_path ON api_endpoints(endpoint_path);
CREATE INDEX idx_api_logs_endpoint ON api_access_logs(endpoint_id);
CREATE INDEX idx_api_logs_timestamp ON api_access_logs(access_timestamp DESC);

-- ==============================================================================
-- MATERIALIZED VIEWS FOR FAST ANALYTICS
-- ==============================================================================

-- Discipline-wise standards summary
CREATE MATERIALIZED VIEW mv_discipline_standards_summary AS
SELECT 
    d.discipline_id,
    d.discipline_name,
    d.display_name,
    COUNT(DISTINCT es.standard_id) as total_standards,
    COUNT(DISTINCT CASE WHEN es.is_validated THEN es.standard_id END) as validated_standards,
    AVG(es.validation_score) as avg_validation_score,
    COUNT(DISTINCT es.document_id) as total_documents,
    COUNT(DISTINCT ss.source_id) as total_sources,
    AVG(ss.quality_score) as avg_source_quality,
    COUNT(DISTINCT cm.competency_id) as total_competencies,
    MAX(es.processed_timestamp) as last_updated
FROM disciplines d
LEFT JOIN educational_standards es ON d.discipline_id = es.discipline_id
LEFT JOIN retrieved_documents rd ON es.document_id = rd.document_id
LEFT JOIN standards_sources ss ON rd.source_id = ss.source_id
LEFT JOIN competency_mappings cm ON es.standard_id = cm.standard_id
WHERE d.is_active = true
GROUP BY d.discipline_id, d.discipline_name, d.display_name;

-- LLM cost efficiency by discipline
CREATE MATERIALIZED VIEW mv_llm_cost_efficiency AS
SELECT 
    d.discipline_name,
    lus.model_name,
    lus.task_type,
    COUNT(*) as total_requests,
    SUM(lus.total_tokens) as total_tokens,
    SUM(lus.cost_usd) as total_cost,
    AVG(lus.quality_score) as avg_quality,
    AVG(lus.response_time_ms) as avg_response_time,
    AVG(lus.cost_efficiency_ratio) as avg_cost_efficiency,
    DATE_TRUNC('day', lus.usage_timestamp) as usage_date
FROM llm_usage_stats lus
JOIN disciplines d ON lus.discipline_id = d.discipline_id
GROUP BY d.discipline_name, lus.model_name, lus.task_type, DATE_TRUNC('day', lus.usage_timestamp);

-- System performance metrics
CREATE MATERIALIZED VIEW mv_system_performance AS
SELECT 
    d.discipline_name,
    as_table.agent_type,
    COUNT(DISTINCT as_table.session_id) as total_sessions,
    SUM(as_table.tasks_completed) as total_tasks_completed,
    AVG(as_table.success_rate) as avg_success_rate,
    AVG(as_table.processing_time_seconds) as avg_processing_time,
    SUM(as_table.tokens_used) as total_tokens_used,
    SUM(as_table.llm_cost) as total_llm_cost,
    DATE_TRUNC('day', as_table.session_start) as session_date
FROM agent_sessions as_table
JOIN disciplines d ON as_table.discipline_id = d.discipline_id
GROUP BY d.discipline_name, as_table.agent_type, DATE_TRUNC('day', as_table.session_start);

-- Create refresh schedule for materialized views
-- Note: These would typically be refreshed via cron jobs or scheduled tasks