#!/usr/bin/env python3
"""
Standards Retrieval Engine - Core document download and storage system
Downloads actual standards documents (PDFs, etc.) from authoritative sources
"""

import requests
import os
import json
import time
from pathlib import Path
from datetime import datetime
from typing import Dict, List, Any, Optional
from urllib.parse import urljoin, urlparse
import hashlib
import logging
from dataclasses import dataclass

@dataclass
class StandardsDocument:
    """Represents a standards document"""
    title: str
    url: str
    organization: str
    discipline: str
    document_type: str  # pdf, html, docx, etc.
    file_size: Optional[int] = None
    download_path: Optional[Path] = None
    checksum: Optional[str] = None
    download_time: Optional[datetime] = None
    metadata: Optional[Dict[str, Any]] = None

class StandardsRetrievalEngine:
    """Engine for retrieving actual standards documents from authoritative sources"""
    
    def __init__(self, base_data_dir: Path):
        self.base_data_dir = Path(base_data_dir)
        self.session = requests.Session()
        self.session.headers.update({
            'User-Agent': 'Educational Standards Research System 1.0 (+https://example.com/standards-research)'
        })
        
        # Setup logging
        self.logger = logging.getLogger(__name__)
        
        # UNIFIED DIRECTORY STRUCTURE: Standards/english/Subject/University/Organization/
        self.standards_dir = self.base_data_dir / "Standards"
        self.documents_dir = self.base_data_dir / "Standards" / "english"
        self.processed_dir = self.base_data_dir / "Standards" / "processed"
        
        # Ensure directories exist
        for directory in [self.standards_dir, self.documents_dir, self.processed_dir]:
            directory.mkdir(parents=True, exist_ok=True)
        
        # Standards organizations with actual document sources
        self.standards_sources = self.initialize_standards_sources()
        
        # Download statistics
        self.download_stats = {
            'total_downloaded': 0,
            'successful_downloads': 0,
            'failed_downloads': 0,
            'total_size_mb': 0,
            'by_discipline': {},
            'by_organization': {}
        }
    
    def initialize_standards_sources(self) -> Dict[str, Dict[str, Any]]:
        """Initialize real standards organization sources with document URLs for ALL 19 disciplines"""
        return {
            'Physical_Sciences': {
                'NIST': {
                    'base_url': 'https://www.nist.gov/standardsgov',
                    'documents': [
                        {
                            'title': 'NIST Framework for Improving Critical Infrastructure Cybersecurity',
                            'url': 'https://nvlpubs.nist.gov/nistpubs/CSWP/NIST.CSWP.04162018.pdf',
                            'type': 'pdf'
                        },
                        {
                            'title': 'NIST Physics Laboratory Standards',
                            'url': 'https://www.nist.gov/pml/physics-laboratory',
                            'type': 'html'
                        }
                    ]
                },
                'IEEE': {
                    'base_url': 'https://standards.ieee.org',
                    'documents': [
                        {
                            'title': 'IEEE Standards Style Manual',
                            'url': 'https://mentor.ieee.org/myproject/Public/mytools/draft/styleman.pdf', 
                            'type': 'pdf'
                        }
                    ]
                },
                'AAPT': {
                    'base_url': 'https://www.aapt.org',
                    'documents': [
                        {
                            'title': 'AAPT Physics Education Standards',
                            'url': 'https://www.aapt.org/aboutaapt/organization/policies/physicseducation.cfm',
                            'type': 'html'
                        },
                        {
                            'title': 'Undergraduate Physics Program Guide',
                            'url': 'https://www.aapt.org/resources/policy/upload/UndergradPhysicsProgGuide.pdf',
                            'type': 'pdf'
                        }
                    ]
                },
                'APS': {
                    'base_url': 'https://www.aps.org',
                    'documents': [
                        {
                            'title': 'APS Physics Education Standards',
                            'url': 'https://www.aps.org/programs/education/index.cfm',
                            'type': 'html'
                        }
                    ]
                },
                'College_Board': {
                    'base_url': 'https://apcentral.collegeboard.org',
                    'documents': [
                        {
                            'title': 'AP Physics 1 Course Description',
                            'url': 'https://apcentral.collegeboard.org/media/pdf/ap-physics-1-course-description.pdf',
                            'type': 'pdf'
                        },
                        {
                            'title': 'AP Physics 2 Course Description', 
                            'url': 'https://apcentral.collegeboard.org/media/pdf/ap-physics-2-course-description.pdf',
                            'type': 'pdf'
                        },
                        {
                            'title': 'SAT Physics Subject Test Standards',
                            'url': 'https://collegereadiness.collegeboard.org/sat-subject-tests/subjects/physics',
                            'type': 'html'
                        }
                    ]
                },
                'Physics_Olympiad': {
                    'base_url': 'https://www.aapt.org/physicsteam',
                    'documents': [
                        {
                            'title': 'International Physics Olympiad Syllabus',
                            'url': 'https://www.aapt.org/physicsteam/2019/upload/2019-physics-team-syllabus.pdf',
                            'type': 'pdf'
                        }
                    ]
                }
            },
            'Computer_Science': {
                'ACM': {
                    'base_url': 'https://www.acm.org/education/curricula-recommendations',
                    'documents': [
                        {
                            'title': 'Computing Curricula 2020 (CC2020)',
                            'url': 'https://www.acm.org/binaries/content/assets/education/curricula-recommendations/cc2020.pdf',
                            'type': 'pdf'
                        }
                    ]
                },
                'IEEE_CS': {
                    'base_url': 'https://www.computer.org/education',
                    'documents': [
                        {
                            'title': 'Software Engineering Body of Knowledge (SWEBOK)',
                            'url': 'https://www.computer.org/education/bodies-of-knowledge/software-engineering',
                            'type': 'html'
                        }
                    ]
                }
            },
            'Engineering': {
                'ABET': {
                    'base_url': 'https://www.abet.org',
                    'documents': [
                        {
                            'title': 'Criteria for Accrediting Engineering Programs',
                            'url': 'https://www.abet.org/accreditation/accreditation-criteria/criteria-for-accrediting-engineering-programs-2023-2024/',
                            'type': 'html'
                        }
                    ]
                },
                'ASEE': {
                    'base_url': 'https://www.asee.org',
                    'documents': [
                        {
                            'title': 'Engineering Education Standards',
                            'url': 'https://www.asee.org/public/conferences/1/papers/9/view',
                            'type': 'html'
                        }
                    ]
                },
                'IEEE_Engineering': {
                    'base_url': 'https://www.ieee.org',
                    'documents': [
                        {
                            'title': 'IEEE Engineering Education Standards',
                            'url': 'https://www.ieee.org/education/index.html',
                            'type': 'html'
                        }
                    ]
                }
            },
            'Mathematics': {
                'NCTM': {
                    'base_url': 'https://www.nctm.org',
                    'documents': [
                        {
                            'title': 'Principles and Standards for School Mathematics',
                            'url': 'https://www.nctm.org/Standards-and-Positions/Principles-and-Standards/',
                            'type': 'html'
                        }
                    ]
                }
            },
            'Life_Sciences': {
                'AIBS': {
                    'base_url': 'https://www.aibs.org',
                    'documents': [
                        {
                            'title': 'Vision and Change in Undergraduate Biology Education',
                            'url': 'https://visionandchange.org/finalreport/',
                            'type': 'html'
                        }
                    ]
                },
                'NABT': {
                    'base_url': 'https://www.nabt.org',
                    'documents': [
                        {
                            'title': 'NABT Position Statements on Biology Education',
                            'url': 'https://www.nabt.org/Portals/0/PDFs/Positions/PositionStatement_Evolution.pdf',
                            'type': 'pdf'
                        }
                    ]
                },
                'College_Board_Bio': {
                    'base_url': 'https://apcentral.collegeboard.org',
                    'documents': [
                        {
                            'title': 'AP Biology Course and Exam Description',
                            'url': 'https://apstudents.collegeboard.org/courses/ap-biology',
                            'type': 'html'
                        }
                    ]
                }
            },
            'Health_Sciences': {
                'LCME': {
                    'base_url': 'https://lcme.org',
                    'documents': [
                        {
                            'title': 'Standards for Accreditation of Medical Education Programs',
                            'url': 'https://lcme.org/publications/',
                            'type': 'html'
                        }
                    ]
                },
                'AAMC': {
                    'base_url': 'https://www.aamc.org',
                    'documents': [
                        {
                            'title': 'MCAT Exam Content and Specifications',
                            'url': 'https://www.aamc.org/media/39781/download',
                            'type': 'pdf'
                        },
                        {
                            'title': 'Core Competencies for Entering Medical Students',
                            'url': 'https://www.aamc.org/media/39786/download',
                            'type': 'pdf'
                        },
                        {
                            'title': 'Medical School Admission Requirements Guide',
                            'url': 'https://www.aamc.org/students/applying/requirements',
                            'type': 'html'
                        }
                    ]
                },
                'USMLE': {
                    'base_url': 'https://www.usmle.org',
                    'documents': [
                        {
                            'title': 'USMLE Step 1 Content Outline',
                            'url': 'https://www.usmle.org/sites/default/files/media/USMLE_Step1_Content_Outline.pdf',
                            'type': 'pdf'
                        },
                        {
                            'title': 'USMLE Step 2 CK Content Outline',
                            'url': 'https://www.usmle.org/sites/default/files/media/USMLE_Step2CK_Content_Outline.pdf',
                            'type': 'pdf'
                        },
                        {
                            'title': 'USMLE Step 3 Content Outline',
                            'url': 'https://www.usmle.org/sites/default/files/media/USMLE_Step3_Content_Outline.pdf',
                            'type': 'pdf'
                        }
                    ]
                },
                'WHO': {
                    'base_url': 'https://www.who.int',
                    'documents': [
                        {
                            'title': 'WHO Standards for Health Professional Education',
                            'url': 'https://www.who.int/publications/i/item/9789241549899',
                            'type': 'html'
                        },
                        {
                            'title': 'Global Standards for Medical Education',
                            'url': 'https://www.who.int/hrh/education/global_standards/en/',
                            'type': 'html'
                        }
                    ]
                },
                'ACGME': {
                    'base_url': 'https://www.acgme.org',
                    'documents': [
                        {
                            'title': 'ACGME Common Program Requirements',
                            'url': 'https://www.acgme.org/globalassets/pfassets/programrequirements/cprresidency2019.pdf',
                            'type': 'pdf'
                        }
                    ]
                },
                'NBME': {
                    'base_url': 'https://www.nbme.org',
                    'documents': [
                        {
                            'title': 'NBME Assessment Standards',
                            'url': 'https://www.nbme.org/about-nbme/mission-vision',
                            'type': 'html'
                        }
                    ]
                }
            },
            'Earth_Sciences': {
                'AGI': {
                    'base_url': 'https://www.americangeosciences.org',
                    'documents': [
                        {
                            'title': 'Earth Science Education Standards',
                            'url': 'https://www.americangeosciences.org/education/k12-education/earth-science-standards',
                            'type': 'html'
                        }
                    ]
                }
            },
            'Environmental_Science': {
                'EPA': {
                    'base_url': 'https://www.epa.gov',
                    'documents': [
                        {
                            'title': 'Environmental Education Guidelines',
                            'url': 'https://www.epa.gov/education/environmental-education-guidelines',
                            'type': 'html'
                        }
                    ]
                },
                'NAAEE': {
                    'base_url': 'https://naaee.org',
                    'documents': [
                        {
                            'title': 'Guidelines for Excellence Environmental Education',
                            'url': 'https://naaee.org/eepro/research/library/guidelines-excellence-series',
                            'type': 'html'
                        }
                    ]
                }
            },
            'Agricultural_Sciences': {
                'USDA': {
                    'base_url': 'https://www.usda.gov',
                    'documents': [
                        {
                            'title': 'Agricultural Education Standards',
                            'url': 'https://www.usda.gov/topics/education',
                            'type': 'html'
                        }
                    ]
                },
                'NAAE': {
                    'base_url': 'https://www.naae.org',
                    'documents': [
                        {
                            'title': 'Agricultural Education Standards',
                            'url': 'https://www.naae.org/teachag/standards.cfm',
                            'type': 'html'
                        }
                    ]
                }
            },
            'Economics': {
                'AEA': {
                    'base_url': 'https://www.aeaweb.org',
                    'documents': [
                        {
                            'title': 'Economics Education Standards',
                            'url': 'https://www.aeaweb.org/resources/students/what-is-economics',
                            'type': 'html'
                        }
                    ]
                }
            },
            'Business': {
                'AACSB': {
                    'base_url': 'https://www.aacsb.edu',
                    'documents': [
                        {
                            'title': 'AACSB Business Accreditation Standards',
                            'url': 'https://www.aacsb.edu/accreditation/standards',
                            'type': 'html'
                        }
                    ]
                }
            },
            'Social_Sciences': {
                'NCSS': {
                    'base_url': 'https://www.socialstudies.org',
                    'documents': [
                        {
                            'title': 'National Social Studies Standards',
                            'url': 'https://www.socialstudies.org/standards',
                            'type': 'html'
                        }
                    ]
                }
            },
            'Geography': {
                'NCGE': {
                    'base_url': 'https://www.ncge.org',
                    'documents': [
                        {
                            'title': 'Geography Education Standards',
                            'url': 'https://www.ncge.org/geography-standards',
                            'type': 'html'
                        }
                    ]
                },
                'National_Geography': {
                    'base_url': 'https://www.nationalgeographic.org',
                    'documents': [
                        {
                            'title': 'National Geography Standards',
                            'url': 'https://www.nationalgeographic.org/education/standards/',
                            'type': 'html'
                        }
                    ]
                }
            },
            'History': {
                'NCHS': {
                    'base_url': 'https://www.nchs.ucla.edu',
                    'documents': [
                        {
                            'title': 'National History Education Standards',
                            'url': 'https://www.nchs.ucla.edu/history-standards',
                            'type': 'html'
                        }
                    ]
                },
                'NCSS_History': {
                    'base_url': 'https://www.socialstudies.org',
                    'documents': [
                        {
                            'title': 'NCSS Thematic Standards for History',
                            'url': 'https://www.socialstudies.org/standards/strands',
                            'type': 'html'
                        }
                    ]
                }
            },
            'Art': {
                'NAEA': {
                    'base_url': 'https://www.arteducators.org',
                    'documents': [
                        {
                            'title': 'National Visual Arts Standards',
                            'url': 'https://www.arteducators.org/learn-tools/national-visual-arts-standards',
                            'type': 'html'
                        }
                    ]
                }
            },
            'Literature': {
                'NCTE': {
                    'base_url': 'https://ncte.org',
                    'documents': [
                        {
                            'title': 'English Language Arts Standards',
                            'url': 'https://ncte.org/what-we-do/standards/',
                            'type': 'html'
                        }
                    ]
                }
            },
            'Philosophy': {
                'APA': {
                    'base_url': 'https://www.apaonline.org',
                    'documents': [
                        {
                            'title': 'Philosophy Education Standards',
                            'url': 'https://www.apaonline.org/page/teaching',
                            'type': 'html'
                        }
                    ]
                },
                'Philosophy_Teaching': {
                    'base_url': 'https://www.apa.org',
                    'documents': [
                        {
                            'title': 'Teaching Philosophy Standards',
                            'url': 'https://www.apa.org/science/about/psa/2017/10/teaching-philosophy',
                            'type': 'html'
                        }
                    ]
                }
            },
            'Law': {
                'ABA': {
                    'base_url': 'https://www.americanbar.org',
                    'documents': [
                        {
                            'title': 'ABA Law School Accreditation Standards',
                            'url': 'https://www.americanbar.org/groups/legal_education/resources/standards/',
                            'type': 'html'
                        }
                    ]
                }
            },
            'Education': {
                'CAEP': {
                    'base_url': 'https://caepnet.org',
                    'documents': [
                        {
                            'title': 'CAEP Accreditation Standards',
                            'url': 'https://caepnet.org/standards',
                            'type': 'html'
                        }
                    ]
                }
            }
        }
    
    def retrieve_standards_for_discipline(self, discipline: str) -> List[StandardsDocument]:
        """Retrieve all available standards documents for a discipline"""
        
        self.logger.info(f"Starting standards retrieval for {discipline}")
        
        if discipline not in self.standards_sources:
            self.logger.warning(f"No sources configured for discipline: {discipline}")
            return []
        
        # Create directory structure mirroring Books: english/subject/University/organization
        subject_mapping = {
            'Physical_Sciences': 'Physics',
            'Computer_Science': 'Computer science', 
            'Life_Sciences': 'Biology',
            'Health_Sciences': 'Medicine',
            'Engineering': 'Engineering',
            'Mathematics': 'Mathematics',
            'Earth_Sciences': 'Earth Sciences',
            'Environmental_Science': 'Environmental Science',
            'Agricultural_Sciences': 'Agriculture',
            'Economics': 'Economics',
            'Business': 'Business',
            'Social_Sciences': 'Sociology',
            'Geography': 'Geography',
            'History': 'History',
            'Art': 'Art',
            'Literature': 'Literature',
            'Philosophy': 'Philosophy',
            'Law': 'Law',
            'Education': 'Education'
        }
        
        subject_name = subject_mapping.get(discipline, discipline)
        discipline_dir = self.documents_dir / subject_name / "University"
        discipline_dir.mkdir(parents=True, exist_ok=True)
        
        retrieved_documents = []
        
        # Process each organization for this discipline
        for org_name, org_config in self.standards_sources[discipline].items():
            self.logger.info(f"Processing {org_name} for {discipline}")
            
            org_dir = discipline_dir / org_name
            org_dir.mkdir(parents=True, exist_ok=True)
            
            # Download documents from this organization
            for doc_info in org_config.get('documents', []):
                try:
                    document = self.download_document(
                        title=doc_info['title'],
                        url=doc_info['url'],
                        organization=org_name,
                        discipline=discipline,
                        document_type=doc_info['type'],
                        download_dir=org_dir
                    )
                    
                    if document:
                        retrieved_documents.append(document)
                        self.logger.info(f"Successfully retrieved: {document.title}")
                    
                except Exception as e:
                    self.logger.error(f"Failed to retrieve {doc_info['title']}: {e}")
                    self.download_stats['failed_downloads'] += 1
                    continue
        
        # Update statistics
        if discipline not in self.download_stats['by_discipline']:
            self.download_stats['by_discipline'][discipline] = 0
        self.download_stats['by_discipline'][discipline] += len(retrieved_documents)
        
        self.logger.info(f"Retrieved {len(retrieved_documents)} documents for {discipline}")
        return retrieved_documents
    
    def download_document(self, title: str, url: str, organization: str, 
                         discipline: str, document_type: str, download_dir: Path) -> Optional[StandardsDocument]:
        """Download a single standards document"""
        
        try:
            # Clean filename
            safe_title = self.sanitize_filename(title)
            
            if document_type == 'pdf':
                filename = f"{safe_title}.pdf"
            elif document_type == 'html':
                filename = f"{safe_title}.html"
            else:
                filename = f"{safe_title}.{document_type}"
            
            file_path = download_dir / filename
            
            # Check if already downloaded
            if file_path.exists():
                self.logger.info(f"Document already exists: {filename}")
                return self.create_document_record(title, url, organization, discipline, 
                                                 document_type, file_path)
            
            # Download the document
            self.logger.info(f"Downloading: {title} from {url}")
            
            response = self.session.get(url, timeout=30, stream=True)
            response.raise_for_status()
            
            # Write to file
            total_size = 0
            with open(file_path, 'wb') as f:
                for chunk in response.iter_content(chunk_size=8192):
                    if chunk:
                        f.write(chunk)
                        total_size += len(chunk)
            
            # Calculate checksum
            checksum = self.calculate_checksum(file_path)
            
            # Create document record
            document = StandardsDocument(
                title=title,
                url=url,
                organization=organization,
                discipline=discipline,
                document_type=document_type,
                file_size=total_size,
                download_path=file_path,
                checksum=checksum,
                download_time=datetime.now(),
                metadata={
                    'content_type': response.headers.get('content-type'),
                    'server': response.headers.get('server'),
                    'original_url': url
                }
            )
            
            # Update statistics
            self.download_stats['successful_downloads'] += 1
            self.download_stats['total_downloaded'] += 1
            self.download_stats['total_size_mb'] += total_size / (1024 * 1024)
            
            if organization not in self.download_stats['by_organization']:
                self.download_stats['by_organization'][organization] = 0
            self.download_stats['by_organization'][organization] += 1
            
            # Save metadata
            self.save_document_metadata(document)
            
            self.logger.info(f"Downloaded {title} ({total_size/1024:.1f} KB)")
            return document
            
        except requests.exceptions.RequestException as e:
            self.logger.error(f"Network error downloading {title}: {e}")
            return None
        except Exception as e:
            self.logger.error(f"Error downloading {title}: {e}")
            return None
    
    def create_document_record(self, title: str, url: str, organization: str, 
                             discipline: str, document_type: str, file_path: Path) -> StandardsDocument:
        """Create a document record for existing file"""
        
        file_size = file_path.stat().st_size if file_path.exists() else 0
        checksum = self.calculate_checksum(file_path) if file_path.exists() else None
        
        return StandardsDocument(
            title=title,
            url=url,
            organization=organization,
            discipline=discipline,
            document_type=document_type,
            file_size=file_size,
            download_path=file_path,
            checksum=checksum,
            download_time=datetime.now(),
            metadata={'status': 'existing_file'}
        )
    
    def sanitize_filename(self, filename: str) -> str:
        """Sanitize filename for filesystem"""
        # Remove invalid characters
        invalid_chars = '<>:"/\\|?*'
        for char in invalid_chars:
            filename = filename.replace(char, '_')
        
        # Limit length
        if len(filename) > 100:
            filename = filename[:100]
        
        return filename.strip()
    
    def calculate_checksum(self, file_path: Path) -> str:
        """Calculate SHA-256 checksum of file"""
        if not file_path.exists():
            return ""
        
        hash_sha256 = hashlib.sha256()
        with open(file_path, "rb") as f:
            for chunk in iter(lambda: f.read(4096), b""):
                hash_sha256.update(chunk)
        return hash_sha256.hexdigest()
    
    def save_document_metadata(self, document: StandardsDocument):
        """Save document metadata to JSON file"""
        metadata_dir = self.processed_dir / document.discipline / document.organization
        metadata_dir.mkdir(parents=True, exist_ok=True)
        
        safe_title = self.sanitize_filename(document.title)
        metadata_file = metadata_dir / f"{safe_title}_metadata.json"
        
        metadata = {
            'title': document.title,
            'url': document.url,
            'organization': document.organization,
            'discipline': document.discipline,
            'document_type': document.document_type,
            'file_size': document.file_size,
            'download_path': str(document.download_path) if document.download_path else None,
            'checksum': document.checksum,
            'download_time': document.download_time.isoformat() if document.download_time else None,
            'metadata': document.metadata
        }
        
        with open(metadata_file, 'w') as f:
            json.dump(metadata, f, indent=2)
    
    def retrieve_all_disciplines(self) -> Dict[str, List[StandardsDocument]]:
        """Retrieve standards for all configured disciplines"""
        
        self.logger.info("Starting complete standards retrieval for all disciplines")
        
        all_results = {}
        
        for discipline in self.standards_sources.keys():
            self.logger.info(f"Processing discipline: {discipline}")
            
            try:
                documents = self.retrieve_standards_for_discipline(discipline)
                all_results[discipline] = documents
                
                # Brief pause between disciplines
                time.sleep(1)
                
            except Exception as e:
                self.logger.error(f"Failed to process {discipline}: {e}")
                all_results[discipline] = []
        
        # Generate summary report
        self.generate_retrieval_report(all_results)
        
        return all_results
    
    def generate_retrieval_report(self, results: Dict[str, List[StandardsDocument]]):
        """Generate comprehensive retrieval report"""
        
        report_file = self.base_data_dir / "standards_retrieval_report.json"
        
        report = {
            'generation_time': datetime.now().isoformat(),
            'statistics': self.download_stats,
            'disciplines_processed': len(results),
            'total_documents_retrieved': sum(len(docs) for docs in results.values()),
            'by_discipline': {},
            'by_organization': {},
            'file_types': {},
            'summary': {
                'successful_disciplines': len([d for d, docs in results.items() if len(docs) > 0]),
                'total_file_size_mb': self.download_stats['total_size_mb'],
                'average_documents_per_discipline': sum(len(docs) for docs in results.values()) / len(results) if results else 0
            }
        }
        
        # Detailed breakdown
        for discipline, documents in results.items():
            discipline_info = {
                'document_count': len(documents),
                'organizations': list(set(doc.organization for doc in documents)),
                'file_types': list(set(doc.document_type for doc in documents)),
                'total_size_mb': sum(doc.file_size or 0 for doc in documents) / (1024 * 1024),
                'documents': [
                    {
                        'title': doc.title,
                        'organization': doc.organization,
                        'type': doc.document_type,
                        'size_kb': (doc.file_size or 0) / 1024,
                        'file_path': str(doc.download_path) if doc.download_path else None
                    }
                    for doc in documents
                ]
            }
            report['by_discipline'][discipline] = discipline_info
        
        # Save report
        with open(report_file, 'w') as f:
            json.dump(report, f, indent=2)
        
        self.logger.info(f"Generated retrieval report: {report_file}")
        
        # Print summary
        print(f"\n📊 STANDARDS RETRIEVAL COMPLETE")
        print(f"=" * 50)
        print(f"Disciplines Processed: {report['disciplines_processed']}")
        print(f"Documents Retrieved: {report['total_documents_retrieved']}")
        print(f"Total Size: {report['summary']['total_file_size_mb']:.1f} MB")
        print(f"Success Rate: {self.download_stats['successful_downloads']}/{self.download_stats['total_downloaded']}")
        print(f"Report saved: {report_file}")
    
    def get_retrieval_status(self) -> Dict[str, Any]:
        """Get current retrieval status"""
        return {
            'download_stats': self.download_stats.copy(),
            'configured_disciplines': list(self.standards_sources.keys()),
            'total_sources': sum(len(orgs) for orgs in self.standards_sources.values()),
            'base_directory': str(self.base_data_dir)
        }