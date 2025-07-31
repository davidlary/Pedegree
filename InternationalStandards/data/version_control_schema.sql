-- Version Control Extended Schema for International Standards Retrieval System
-- Additional tables for comprehensive version control and change tracking
-- Author: Autonomous AI Development System

-- ==============================================================================
-- CHANGESET MANAGEMENT TABLES
-- ==============================================================================

-- Changesets for grouping related changes
CREATE TABLE IF NOT EXISTS changesets (
    changeset_id VARCHAR(100) PRIMARY KEY,
    description TEXT NOT NULL,
    timestamp TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    status VARCHAR(20) DEFAULT 'pending', -- 'pending', 'committed', 'rollback', 'archived'
    discipline_scope INTEGER[] DEFAULT '{}', -- Array of discipline_ids affected
    rollback_available BOOLEAN DEFAULT TRUE,
    change_count INTEGER DEFAULT 0,
    created_by VARCHAR(100) DEFAULT 'system',
    committed_timestamp TIMESTAMP,
    rollback_timestamp TIMESTAMP,
    metadata JSONB,
    INDEX_SCOPE -- Index for discipline scope queries
);

-- Version metadata for enhanced tracking
CREATE TABLE IF NOT EXISTS version_metadata (
    metadata_id SERIAL PRIMARY KEY,
    version_id INTEGER NOT NULL REFERENCES data_versions(version_id),
    metadata_key VARCHAR(100) NOT NULL,
    metadata_value TEXT,
    metadata_type VARCHAR(50) DEFAULT 'string', -- 'string', 'number', 'boolean', 'json'
    created_timestamp TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    UNIQUE(version_id, metadata_key)
);

-- Change impact analysis
CREATE TABLE IF NOT EXISTS change_impact (
    impact_id SERIAL PRIMARY KEY,
    changeset_id VARCHAR(100) NOT NULL REFERENCES changesets(changeset_id),
    affected_table VARCHAR(100) NOT NULL,
    affected_records INTEGER[] DEFAULT '{}',
    impact_type VARCHAR(50) NOT NULL, -- 'direct', 'cascade', 'reference'
    severity_level INTEGER DEFAULT 1, -- 1-5 scale
    description TEXT,
    mitigation_steps TEXT[],
    created_timestamp TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

-- Rollback procedures and history
CREATE TABLE IF NOT EXISTS rollback_procedures (
    procedure_id SERIAL PRIMARY KEY,
    changeset_id VARCHAR(100) NOT NULL REFERENCES changesets(changeset_id),
    rollback_order INTEGER NOT NULL,
    target_table VARCHAR(100) NOT NULL,
    target_record_id INTEGER NOT NULL,
    rollback_action VARCHAR(20) NOT NULL, -- 'restore', 'delete', 'update'
    rollback_sql TEXT,
    rollback_parameters JSONB,
    execution_status VARCHAR(20) DEFAULT 'pending', -- 'pending', 'executed', 'failed'
    executed_timestamp TIMESTAMP,
    error_message TEXT
);

-- ==============================================================================
-- AUDIT AND COMPLIANCE TABLES  
-- ==============================================================================

-- Audit trail for sensitive operations
CREATE TABLE IF NOT EXISTS audit_trail (
    audit_id SERIAL PRIMARY KEY,
    event_type VARCHAR(50) NOT NULL, -- 'data_access', 'modification', 'export', 'api_call'
    table_name VARCHAR(100),
    record_id INTEGER,
    discipline_id INTEGER REFERENCES disciplines(discipline_id),
    user_identifier VARCHAR(100) NOT NULL,
    ip_address INET,
    user_agent TEXT,
    event_timestamp TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    event_details JSONB,
    compliance_flags TEXT[], -- Array of compliance requirements met
    retention_until TIMESTAMP,
    archived BOOLEAN DEFAULT FALSE
);

-- Data lineage tracking
CREATE TABLE IF NOT EXISTS data_lineage (
    lineage_id SERIAL PRIMARY KEY,
    source_table VARCHAR(100) NOT NULL,
    source_record_id INTEGER NOT NULL,
    target_table VARCHAR(100) NOT NULL,
    target_record_id INTEGER NOT NULL,
    relationship_type VARCHAR(50) NOT NULL, -- 'derived_from', 'aggregated_from', 'transformed_from'
    transformation_method VARCHAR(100),
    transformation_timestamp TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    confidence_score DECIMAL(4,3) DEFAULT 1.000,
    metadata JSONB
);

-- ==============================================================================
-- PERFORMANCE AND MONITORING TABLES
-- ==============================================================================

-- Version control performance metrics
CREATE TABLE IF NOT EXISTS version_performance (
    metric_id SERIAL PRIMARY KEY,
    measurement_date DATE DEFAULT CURRENT_DATE,
    table_name VARCHAR(100),
    discipline_id INTEGER REFERENCES disciplines(discipline_id),
    total_versions INTEGER DEFAULT 0,
    versions_added_today INTEGER DEFAULT 0,
    avg_version_size_kb DECIMAL(10,2) DEFAULT 0.00,
    rollbacks_performed INTEGER DEFAULT 0,
    cleanup_operations INTEGER DEFAULT 0,
    storage_usage_mb DECIMAL(10,2) DEFAULT 0.00,
    query_performance_ms DECIMAL(8,2) DEFAULT 0.00,
    UNIQUE(measurement_date, table_name, discipline_id)
);

-- Change frequency analysis
CREATE TABLE IF NOT EXISTS change_frequency (
    frequency_id SERIAL PRIMARY KEY,
    table_name VARCHAR(100) NOT NULL,
    record_id INTEGER NOT NULL,
    discipline_id INTEGER REFERENCES disciplines(discipline_id),
    analysis_period_start TIMESTAMP NOT NULL,
    analysis_period_end TIMESTAMP NOT NULL,
    total_changes INTEGER DEFAULT 0,
    change_types JSONB, -- {insert: 1, update: 5, delete: 0}
    avg_time_between_changes INTERVAL,
    change_velocity DECIMAL(8,4) DEFAULT 0.0000, -- changes per hour
    volatility_score DECIMAL(4,3) DEFAULT 0.000, -- how frequently record changes
    last_analyzed TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

-- ==============================================================================
-- INDEXES FOR OPTIMAL VERSION CONTROL PERFORMANCE
-- ==============================================================================

-- Changeset indexes
CREATE INDEX idx_changesets_status ON changesets(status);
CREATE INDEX idx_changesets_timestamp ON changesets(timestamp DESC);
CREATE INDEX idx_changesets_discipline_scope ON changesets USING GIN(discipline_scope);

-- Version metadata indexes
CREATE INDEX idx_version_metadata_version ON version_metadata(version_id);
CREATE INDEX idx_version_metadata_key ON version_metadata(metadata_key);

-- Change impact indexes
CREATE INDEX idx_change_impact_changeset ON change_impact(changeset_id);
CREATE INDEX idx_change_impact_table ON change_impact(affected_table);
CREATE INDEX idx_change_impact_severity ON change_impact(severity_level DESC);

-- Rollback procedure indexes
CREATE INDEX idx_rollback_procedures_changeset ON rollback_procedures(changeset_id);
CREATE INDEX idx_rollback_procedures_order ON rollback_procedures(rollback_order);
CREATE INDEX idx_rollback_procedures_status ON rollback_procedures(execution_status);

-- Audit trail indexes
CREATE INDEX idx_audit_trail_timestamp ON audit_trail(event_timestamp DESC);
CREATE INDEX idx_audit_trail_user ON audit_trail(user_identifier);
CREATE INDEX idx_audit_trail_table_record ON audit_trail(table_name, record_id);
CREATE INDEX idx_audit_trail_discipline ON audit_trail(discipline_id);
CREATE INDEX idx_audit_trail_event_type ON audit_trail(event_type);

-- Data lineage indexes
CREATE INDEX idx_data_lineage_source ON data_lineage(source_table, source_record_id);
CREATE INDEX idx_data_lineage_target ON data_lineage(target_table, target_record_id);
CREATE INDEX idx_data_lineage_type ON data_lineage(relationship_type);

-- Performance monitoring indexes
CREATE INDEX idx_version_performance_date ON version_performance(measurement_date DESC);
CREATE INDEX idx_version_performance_table ON version_performance(table_name);
CREATE INDEX idx_version_performance_discipline ON version_performance(discipline_id);

CREATE INDEX idx_change_frequency_table_record ON change_frequency(table_name, record_id);
CREATE INDEX idx_change_frequency_period ON change_frequency(analysis_period_start, analysis_period_end);
CREATE INDEX idx_change_frequency_volatility ON change_frequency(volatility_score DESC);

-- ==============================================================================
-- MATERIALIZED VIEWS FOR VERSION CONTROL ANALYTICS
-- ==============================================================================

-- Version control summary by discipline
CREATE MATERIALIZED VIEW mv_version_control_summary AS
SELECT 
    d.discipline_id,
    d.discipline_name,
    d.display_name,
    COUNT(DISTINCT dv.version_id) as total_versions,
    COUNT(DISTINCT dv.table_name) as tables_with_versions,
    COUNT(DISTINCT CASE WHEN dv.change_type = 'insert' THEN dv.version_id END) as inserts,
    COUNT(DISTINCT CASE WHEN dv.change_type = 'update' THEN dv.version_id END) as updates,
    COUNT(DISTINCT CASE WHEN dv.change_type = 'delete' THEN dv.version_id END) as deletes,
    MAX(dv.change_timestamp) as last_change,
    COUNT(DISTINCT cs.changeset_id) as total_changesets,
    COUNT(DISTINCT CASE WHEN cs.status = 'rollback' THEN cs.changeset_id END) as rollbacks
FROM disciplines d
LEFT JOIN data_versions dv ON d.discipline_id = dv.discipline_id
LEFT JOIN changesets cs ON d.discipline_id = ANY(cs.discipline_scope)
WHERE d.is_active = true
GROUP BY d.discipline_id, d.discipline_name, d.display_name;

-- Change velocity by table
CREATE MATERIALIZED VIEW mv_change_velocity AS
SELECT 
    table_name,
    COUNT(*) as total_changes,
    COUNT(DISTINCT record_id) as unique_records_changed,
    MIN(change_timestamp) as first_change,
    MAX(change_timestamp) as last_change,
    EXTRACT(EPOCH FROM (MAX(change_timestamp) - MIN(change_timestamp))) / 3600 as timespan_hours,
    COUNT(*) / GREATEST(EXTRACT(EPOCH FROM (MAX(change_timestamp) - MIN(change_timestamp))) / 3600, 1) as changes_per_hour,
    AVG(CASE WHEN change_type = 'update' THEN 1 ELSE 0 END) as update_ratio
FROM data_versions
WHERE change_timestamp >= CURRENT_DATE - INTERVAL '30 days'
GROUP BY table_name
HAVING COUNT(*) > 10;

-- Version control health metrics
CREATE MATERIALIZED VIEW mv_version_control_health AS
SELECT 
    CURRENT_DATE as report_date,
    COUNT(DISTINCT dv.version_id) as total_versions,
    COUNT(DISTINCT cs.changeset_id) as total_changesets,
    COUNT(DISTINCT CASE WHEN cs.status = 'committed' THEN cs.changeset_id END) as committed_changesets,
    COUNT(DISTINCT CASE WHEN cs.status = 'rollback' THEN cs.changeset_id END) as rolled_back_changesets,
    ROUND(
        COUNT(DISTINCT CASE WHEN cs.status = 'committed' THEN cs.changeset_id END) * 100.0 / 
        NULLIF(COUNT(DISTINCT cs.changeset_id), 0), 2
    ) as commit_success_rate,
    AVG(vp.storage_usage_mb) as avg_storage_usage_mb,
    AVG(vp.query_performance_ms) as avg_query_performance_ms
FROM data_versions dv
LEFT JOIN changesets cs ON 1=1  -- Cross join for overall stats
LEFT JOIN version_performance vp ON vp.measurement_date = CURRENT_DATE;

-- ==============================================================================
-- TRIGGERS FOR AUTOMATIC VERSION CONTROL
-- ==============================================================================

-- Function to automatically track changes
CREATE OR REPLACE FUNCTION track_data_changes()
RETURNS TRIGGER AS $$
DECLARE
    old_values JSONB;
    new_values JSONB;
    changed_fields TEXT[];
    discipline_id_val INTEGER;
BEGIN
    -- Determine discipline_id if available
    discipline_id_val := NULL;
    IF TG_TABLE_NAME IN ('educational_standards', 'competency_mappings', 'retrieved_documents') THEN
        IF NEW.discipline_id IS NOT NULL THEN
            discipline_id_val := NEW.discipline_id;
        ELSIF OLD IS NOT NULL AND OLD.discipline_id IS NOT NULL THEN
            discipline_id_val := OLD.discipline_id;
        END IF;
    END IF;

    -- Handle different operation types
    IF TG_OP = 'INSERT' THEN
        new_values := to_jsonb(NEW);
        changed_fields := array(SELECT jsonb_object_keys(new_values));
        
        INSERT INTO data_versions 
        (table_name, record_id, discipline_id, change_type, changed_fields, 
         new_values, change_timestamp, changed_by, version_hash, is_active_version)
        VALUES 
        (TG_TABLE_NAME, 
         CASE TG_TABLE_NAME 
            WHEN 'disciplines' THEN NEW.discipline_id
            WHEN 'standards_sources' THEN NEW.source_id
            WHEN 'retrieved_documents' THEN NEW.document_id
            WHEN 'educational_standards' THEN NEW.standard_id
            WHEN 'competency_mappings' THEN NEW.competency_id
         END,
         discipline_id_val, 'insert', changed_fields, new_values, 
         CURRENT_TIMESTAMP, 'trigger', 
         encode(sha256(new_values::text::bytea), 'hex'), TRUE);
        
        RETURN NEW;
        
    ELSIF TG_OP = 'UPDATE' THEN
        old_values := to_jsonb(OLD);
        new_values := to_jsonb(NEW);
        
        -- Find changed fields
        SELECT array_agg(key) INTO changed_fields
        FROM jsonb_each(new_values) n
        WHERE NOT EXISTS (
            SELECT 1 FROM jsonb_each(old_values) o 
            WHERE o.key = n.key AND o.value = n.value
        );
        
        IF array_length(changed_fields, 1) > 0 THEN
            INSERT INTO data_versions 
            (table_name, record_id, discipline_id, change_type, changed_fields,
             old_values, new_values, change_timestamp, changed_by, version_hash, is_active_version)
            VALUES 
            (TG_TABLE_NAME,
             CASE TG_TABLE_NAME 
                WHEN 'disciplines' THEN NEW.discipline_id
                WHEN 'standards_sources' THEN NEW.source_id
                WHEN 'retrieved_documents' THEN NEW.document_id
                WHEN 'educational_standards' THEN NEW.standard_id
                WHEN 'competency_mappings' THEN NEW.competency_id
             END,
             discipline_id_val, 'update', changed_fields, old_values, new_values,
             CURRENT_TIMESTAMP, 'trigger',
             encode(sha256((old_values::text || new_values::text)::bytea), 'hex'), TRUE);
        END IF;
        
        RETURN NEW;
        
    ELSIF TG_OP = 'DELETE' THEN
        old_values := to_jsonb(OLD);
        changed_fields := array(SELECT jsonb_object_keys(old_values));
        
        INSERT INTO data_versions 
        (table_name, record_id, discipline_id, change_type, changed_fields,
         old_values, change_timestamp, changed_by, version_hash, is_active_version)
        VALUES 
        (TG_TABLE_NAME,
         CASE TG_TABLE_NAME 
            WHEN 'disciplines' THEN OLD.discipline_id
            WHEN 'standards_sources' THEN OLD.source_id
            WHEN 'retrieved_documents' THEN OLD.document_id
            WHEN 'educational_standards' THEN OLD.standard_id
            WHEN 'competency_mappings' THEN OLD.competency_id
         END,
         discipline_id_val, 'delete', changed_fields, old_values,
         CURRENT_TIMESTAMP, 'trigger',
         encode(sha256(old_values::text::bytea), 'hex'), TRUE);
        
        RETURN OLD;
    END IF;
    
    RETURN NULL;
END;
$$ LANGUAGE plpgsql;

-- Create triggers for automatic version tracking (optional - can be enabled selectively)
-- Uncomment the following lines to enable automatic version tracking:

-- CREATE TRIGGER trigger_disciplines_version_control
--     AFTER INSERT OR UPDATE OR DELETE ON disciplines
--     FOR EACH ROW EXECUTE FUNCTION track_data_changes();

-- CREATE TRIGGER trigger_standards_sources_version_control
--     AFTER INSERT OR UPDATE OR DELETE ON standards_sources
--     FOR EACH ROW EXECUTE FUNCTION track_data_changes();

-- CREATE TRIGGER trigger_educational_standards_version_control
--     AFTER INSERT OR UPDATE OR DELETE ON educational_standards
--     FOR EACH ROW EXECUTE FUNCTION track_data_changes();

-- CREATE TRIGGER trigger_competency_mappings_version_control
--     AFTER INSERT OR UPDATE OR DELETE ON competency_mappings
--     FOR EACH ROW EXECUTE FUNCTION track_data_changes();

-- ==============================================================================
-- MAINTENANCE PROCEDURES
-- ==============================================================================

-- Procedure to refresh version control materialized views
CREATE OR REPLACE FUNCTION refresh_version_control_views()
RETURNS VOID AS $$
BEGIN
    REFRESH MATERIALIZED VIEW mv_version_control_summary;
    REFRESH MATERIALIZED VIEW mv_change_velocity;
    REFRESH MATERIALIZED VIEW mv_version_control_health;
    
    -- Log the refresh
    INSERT INTO audit_trail (event_type, user_identifier, event_details)
    VALUES ('maintenance', 'system', '{"action": "refresh_version_control_views"}');
END;
$$ LANGUAGE plpgsql;

-- Procedure to cleanup old version data
CREATE OR REPLACE FUNCTION cleanup_version_data(days_to_keep INTEGER DEFAULT 90)
RETURNS INTEGER AS $$
DECLARE
    deleted_count INTEGER;
    cutoff_date TIMESTAMP;
BEGIN
    cutoff_date := CURRENT_TIMESTAMP - (days_to_keep || ' days')::INTERVAL;
    
    -- Archive old audit trail entries
    UPDATE audit_trail 
    SET archived = TRUE 
    WHERE event_timestamp < cutoff_date AND NOT archived;
    
    -- Delete old version records (keeping at least one per record)
    WITH versions_to_keep AS (
        SELECT DISTINCT ON (table_name, record_id) version_id
        FROM data_versions
        ORDER BY table_name, record_id, change_timestamp DESC
    )
    DELETE FROM data_versions 
    WHERE change_timestamp < cutoff_date 
    AND version_id NOT IN (SELECT version_id FROM versions_to_keep);
    
    GET DIAGNOSTICS deleted_count = ROW_COUNT;
    
    -- Log the cleanup
    INSERT INTO audit_trail (event_type, user_identifier, event_details)
    VALUES ('maintenance', 'system', 
            json_build_object('action', 'cleanup_version_data', 
                            'deleted_versions', deleted_count,
                            'cutoff_date', cutoff_date));
    
    RETURN deleted_count;
END;
$$ LANGUAGE plpgsql;