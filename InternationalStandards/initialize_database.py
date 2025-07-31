#!/usr/bin/env python3
"""
Database Schema Initialization - NO PLACEHOLDER CODE
Creates all required tables with sample data for testing
"""

import sqlite3
import json
from pathlib import Path
from datetime import datetime

def initialize_database():
    """Initialize database with proper schema and sample data"""
    db_path = Path("data/international_standards.db")
    db_path.parent.mkdir(exist_ok=True)
    
    conn = sqlite3.connect(db_path)
    cursor = conn.cursor()
    
    # Create disciplines table
    cursor.execute("""
        CREATE TABLE IF NOT EXISTS disciplines (
            discipline_id INTEGER PRIMARY KEY,
            discipline_name TEXT UNIQUE NOT NULL,
            display_name TEXT NOT NULL,
            openalex_id TEXT UNIQUE NOT NULL,
            description TEXT,
            priority_level INTEGER DEFAULT 5,
            is_active BOOLEAN DEFAULT TRUE,
            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
        )
    """)
    
    # Insert 19 OpenAlex disciplines
    disciplines = [
        (1, 'Physical_Sciences', 'Physical Sciences', 'physics', 'Physics, Chemistry, Astronomy', 1),
        (2, 'Life_Sciences', 'Life Sciences', 'biology', 'Biology, Ecology, Genetics', 1),
        (3, 'Health_Sciences', 'Health Sciences', 'medicine', 'Medicine, Public Health, Nursing', 1),
        (4, 'Social_Sciences', 'Social Sciences', 'sociology', 'Sociology, Anthropology, Political Science', 2),
        (5, 'Computer_Science', 'Computer Science', 'computer-science', 'AI, Software Engineering, Data Science', 1),
        (6, 'Mathematics', 'Mathematics', 'mathematics', 'Pure Math, Applied Math, Statistics', 1),
        (7, 'Engineering', 'Engineering', 'engineering', 'Mechanical, Electrical, Chemical Engineering', 1),
        (8, 'Business', 'Business', 'business', 'Management, Finance, Marketing', 2),
        (9, 'Economics', 'Economics', 'economics', 'Microeconomics, Macroeconomics, Econometrics', 2),
        (10, 'Geography', 'Geography', 'geography', 'Human Geography, Physical Geography', 3),
        (11, 'Environmental_Science', 'Environmental Science', 'environmental-science', 'Ecology, Climate Science', 2),
        (12, 'Earth_Sciences', 'Earth Sciences', 'earth-sciences', 'Geology, Meteorology, Oceanography', 3),
        (13, 'Agricultural_Sciences', 'Agricultural Sciences', 'agriculture', 'Agronomy, Food Science', 3),
        (14, 'History', 'History', 'history', 'World History, Cultural History', 4),
        (15, 'Philosophy', 'Philosophy', 'philosophy', 'Ethics, Logic, Metaphysics', 4),
        (16, 'Art', 'Art', 'art', 'Fine Arts, Visual Arts, Art History', 4),
        (17, 'Literature', 'Literature', 'literature', 'Comparative Literature, Literary Theory', 4),
        (18, 'Education', 'Education', 'education', 'Pedagogy, Educational Psychology', 3),
        (19, 'Law', 'Law', 'law', 'Constitutional Law, International Law', 3)
    ]
    
    cursor.executemany("""
        INSERT OR REPLACE INTO disciplines 
        (discipline_id, discipline_name, display_name, openalex_id, description, priority_level)
        VALUES (?, ?, ?, ?, ?, ?)
    """, disciplines)
    
    # Create standards table
    cursor.execute("""
        CREATE TABLE IF NOT EXISTS standards (
            id INTEGER PRIMARY KEY,
            title TEXT NOT NULL,
            discipline TEXT NOT NULL,
            organization TEXT NOT NULL,
            quality_score REAL DEFAULT 0.0,
            status TEXT DEFAULT 'active',
            last_updated TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
            created_date TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
            metadata TEXT DEFAULT '{}'
        )
    """)
    
    # Insert sample standards data for testing
    sample_standards = [
        (1, 'Common Core State Standards for Mathematics', 'Mathematics', 'Common Core State Standards', 0.95, 'active'),
        (2, 'Next Generation Science Standards', 'Physical_Sciences', 'NGSS Lead States', 0.92, 'active'),
        (3, 'IEEE Software Engineering Standards', 'Computer_Science', 'IEEE', 0.89, 'active'),
        (4, 'International Baccalaureate Science Curriculum', 'Life_Sciences', 'IB Organization', 0.88, 'active'),
        (5, 'ABET Engineering Accreditation Criteria', 'Engineering', 'ABET', 0.91, 'active')
    ]
    
    cursor.executemany("""
        INSERT OR REPLACE INTO standards 
        (id, title, discipline, organization, quality_score, status)
        VALUES (?, ?, ?, ?, ?, ?)
    """, sample_standards)
    
    conn.commit()
    conn.close()
    
    print(f"✅ Database initialized at {db_path}")
    print(f"✅ Created {len(disciplines)} disciplines")
    print(f"✅ Created {len(sample_standards)} sample standards")

if __name__ == "__main__":
    initialize_database()