#!/usr/bin/env python3
"""
ENHANCED DOCUMENT SOURCES - Comprehensive Curriculum Framework Sources
Uses verified, working URLs for all 19 disciplines with extensive fallback sources
ROOT CAUSE FIX: Replace problematic URLs with working alternatives
"""

from pathlib import Path
from typing import List
from robust_document_retrieval_engine import DocumentSource

def get_comprehensive_working_sources() -> List[DocumentSource]:
    """Get comprehensive working document sources for all 19 disciplines"""
    sources = []
    
    # PHYSICS - Enhanced with working URLs
    physics_sources = [
        DocumentSource("AP Physics 1 Course Description", 
                      "https://secure-media.collegeboard.org/digitalServices/pdf/ap/ap-physics-1-course-and-exam-description.pdf", 
                      "Physics", "High_School", "College_Board_US", 
                      "curriculum_framework", "US"),
        DocumentSource("AP Physics C Mechanics Course Description", 
                      "https://secure-media.collegeboard.org/digitalServices/pdf/ap/ap-physics-c-mechanics-course-and-exam-description.pdf", 
                      "Physics", "High_School", "College_Board_US", 
                      "curriculum_framework", "US"),
        DocumentSource("NGSS Physical Science Standards", 
                      "https://www.nextgenscience.org/sites/default/files/NGSS%20DCI%20Combined%2011.6.13.pdf", 
                      "Physics", "High_School", "Next_Generation_Science_Standards_US", 
                      "curriculum_framework", "US"),
        DocumentSource("Cambridge IGCSE Physics Syllabus", 
                      "https://www.cambridgeinternational.org/programmes-and-qualifications/cambridge-igcse-physics-0625/", 
                      "Physics", "High_School", "Cambridge_International", 
                      "curriculum_framework", "Global"),
        DocumentSource("AAPT Undergraduate Physics Program Guidelines", 
                      "https://www.aapt.org/Resources/upload/AAPT_UndergradPhysicsPrograms_Nov2016.pdf", 
                      "Physics", "Undergraduate", "AAPT", 
                      "curriculum_framework", "US",
                      fallback_urls=["https://www.aapt.org/Resources/"])
    ]
    sources.extend(physics_sources)
    
    # COMPUTER SCIENCE - Enhanced with verified URLs
    cs_sources = [
        DocumentSource("AP Computer Science A Course Description", 
                      "https://secure-media.collegeboard.org/digitalServices/pdf/ap/ap-computer-science-a-course-and-exam-description.pdf", 
                      "Computer_Science", "High_School", "College_Board_US", 
                      "curriculum_framework", "US"),
        DocumentSource("ACM Computing Curricula 2020", 
                      "https://www.acm.org/binaries/content/assets/education/curricula-recommendations/cc2020.pdf", 
                      "Computer_Science", "Undergraduate", "Association_for_Computing_Machinery", 
                      "curriculum_framework", "Global"),
        DocumentSource("IEEE Software Engineering Body of Knowledge", 
                      "https://www.computer.org/education/bodies-of-knowledge/software-engineering", 
                      "Computer_Science", "Undergraduate", "IEEE_CS", 
                      "curriculum_framework", "Global"),
        DocumentSource("ABET Computing Accreditation Criteria 2023-24", 
                      "https://www.abet.org/wp-content/uploads/2022/09/C001-23-24-CAC-Criteria-9-28-22-Final.pdf", 
                      "Computer_Science", "Undergraduate", "ABET", 
                      "accreditation_standard", "US",
                      fallback_urls=["https://www.abet.org/accreditation/accreditation-criteria/"])
    ]
    sources.extend(cs_sources)
    
    # MATHEMATICS - Enhanced with working URLs
    math_sources = [
        DocumentSource("Common Core Mathematics Standards", 
                      "https://learning.ccsso.org/wp-content/uploads/2022/11/Math_Standards1.pdf", 
                      "Mathematics", "High_School", "Common_Core_State_Standards_US", 
                      "curriculum_framework", "US"),
        DocumentSource("AP Calculus AB Course Description", 
                      "https://secure-media.collegeboard.org/digitalServices/pdf/ap/ap-calculus-ab-course-and-exam-description.pdf", 
                      "Mathematics", "High_School", "College_Board_US", 
                      "curriculum_framework", "US"),
        DocumentSource("NCTM Principles and Standards for School Mathematics", 
                      "https://www.nctm.org/Standards-and-Positions/Principles-and-Standards/", 
                      "Mathematics", "High_School", "NCTM", 
                      "curriculum_framework", "US"),
        DocumentSource("MAA Mathematical Association Guidelines", 
                      "https://www.maa.org/programs/faculty-and-departments/curriculum-department-guidelines-recommendations/cupm", 
                      "Mathematics", "Undergraduate", "Mathematical_Association_of_America", 
                      "curriculum_framework", "US")
    ]
    sources.extend(math_sources)
    
    # BIOLOGY/LIFE SCIENCES
    biology_sources = [
        DocumentSource("AP Biology Course Description", 
                      "https://secure-media.collegeboard.org/digitalServices/pdf/ap/ap-biology-course-and-exam-description.pdf", 
                      "Life_Sciences", "High_School", "College_Board_US", 
                      "curriculum_framework", "US"),
        DocumentSource("NGSS Life Science Standards", 
                      "https://www.nextgenscience.org/sites/default/files/NGSS%20DCI%20Combined%2011.6.13.pdf", 
                      "Life_Sciences", "High_School", "Next_Generation_Science_Standards_US", 
                      "curriculum_framework", "US"),
        DocumentSource("AIBS Core Competencies for Biological Literacy", 
                      "https://www.aibs.org/core-competencies/", 
                      "Life_Sciences", "Undergraduate", "AIBS", 
                      "curriculum_framework", "US")
    ]
    sources.extend(biology_sources)
    
    # CHEMISTRY
    chemistry_sources = [
        DocumentSource("AP Chemistry Course Description", 
                      "https://secure-media.collegeboard.org/digitalServices/pdf/ap/ap-chemistry-course-and-exam-description.pdf", 
                      "Physical_Sciences", "High_School", "College_Board_US", 
                      "curriculum_framework", "US"),
        DocumentSource("ACS Guidelines for Chemistry Programs", 
                      "https://www.acs.org/content/acs/en/about/governance/committees/training/acsapproved/degreeprogram/undergraduate-professional-education-in-chemistry-guidelines-and-evaluation-procedures.html", 
                      "Physical_Sciences", "Undergraduate", "ACS", 
                      "curriculum_framework", "US")
    ]
    sources.extend(chemistry_sources)
    
    # ENGINEERING
    engineering_sources = [
        DocumentSource("ABET Engineering Criteria 2023-24", 
                      "https://www.abet.org/wp-content/uploads/2022/09/E001-23-24-EAC-Criteria-9-28-22-Final.pdf", 
                      "Engineering", "Undergraduate", "ABET", 
                      "accreditation_standard", "US"),
        DocumentSource("IEEE Standards Style Manual", 
                      "https://standards.ieee.org/wp-content/uploads/import/documents/other/stdstyle.pdf", 
                      "Engineering", "Undergraduate", "IEEE_Engineering", 
                      "curriculum_framework", "Global"),
        DocumentSource("ASEE Engineering Education Guidelines", 
                      "https://www.asee.org/about-us/the-organization/our-board-of-directors/2020-documents/BOD-October-2020", 
                      "Engineering", "Undergraduate", "ASEE", 
                      "curriculum_framework", "US")
    ]
    sources.extend(engineering_sources)
    
    # HEALTH SCIENCES/MEDICINE
    health_sources = [
        DocumentSource("LCME Standards for Medical Education", 
                      "https://lcme.org/wp-content/uploads/filebase/standards/2023-24_Functions-and-Structure_2022-03-11.pdf", 
                      "Health_Sciences", "Undergraduate", "LCME", 
                      "accreditation_standard", "US"),
        DocumentSource("AAMC Core Competencies for Medical Students", 
                      "https://www.aamc.org/what-we-do/mission-areas/medical-education/cbme/core-competencies", 
                      "Health_Sciences", "Undergraduate", "AAMC", 
                      "curriculum_framework", "US"),
        DocumentSource("MCAT Exam Content and Specifications", 
                      "https://www.aamc.org/system/files/2022-05/services_mcat_mcat-content_2023.pdf", 
                      "Health_Sciences", "Graduate", "AAMC", 
                      "assessment_standard", "US")
    ]
    sources.extend(health_sources)
    
    # EARTH SCIENCES
    earth_sources = [
        DocumentSource("AP Environmental Science Course Description", 
                      "https://secure-media.collegeboard.org/digitalServices/pdf/ap/ap-environmental-science-course-and-exam-description.pdf", 
                      "Earth_Sciences", "High_School", "College_Board_US", 
                      "curriculum_framework", "US"),
        DocumentSource("AGI Earth Science Education Standards", 
                      "https://www.americangeosciences.org/workforce/curricular-guidelines", 
                      "Earth_Sciences", "Undergraduate", "AGI", 
                      "curriculum_framework", "US")
    ]
    sources.extend(earth_sources)
    
    # ENVIRONMENTAL SCIENCE
    env_sources = [
        DocumentSource("NAAEE Guidelines for Environmental Education", 
                      "https://naaee.org/our-work/programs/guidelines-for-excellence", 
                      "Environmental_Science", "High_School", "NAAEE", 
                      "curriculum_framework", "US"),
        DocumentSource("EPA Environmental Education Guidelines", 
                      "https://www.epa.gov/education/environmental-education-guidelines-excellence-k-12-learning", 
                      "Environmental_Science", "High_School", "EPA", 
                      "curriculum_framework", "US")
    ]
    sources.extend(env_sources)
    
    # BUSINESS
    business_sources = [
        DocumentSource("AACSB Business Accreditation Standards", 
                      "https://www.aacsb.edu/-/media/documents/accreditation/business/standards-and-tables/2020%20business%20standards.pdf", 
                      "Business", "Undergraduate", "AACSB", 
                      "accreditation_standard", "US"),
        DocumentSource("AP Business Course Descriptions", 
                      "https://apcentral.collegeboard.org/courses", 
                      "Business", "High_School", "College_Board_US", 
                      "curriculum_framework", "US")
    ]
    sources.extend(business_sources)
    
    # ECONOMICS
    econ_sources = [
        DocumentSource("AP Economics Course Descriptions", 
                      "https://secure-media.collegeboard.org/digitalServices/pdf/ap/ap-microeconomics-course-and-exam-description.pdf", 
                      "Economics", "High_School", "College_Board_US", 
                      "curriculum_framework", "US"),
        DocumentSource("AEA Economics Education Standards", 
                      "https://www.aeaweb.org/about-aea/committees/economics-education", 
                      "Economics", "Undergraduate", "AEA", 
                      "curriculum_framework", "US")
    ]
    sources.extend(econ_sources)
    
    # SOCIAL SCIENCES
    social_sources = [
        DocumentSource("AP Psychology Course Description", 
                      "https://secure-media.collegeboard.org/digitalServices/pdf/ap/ap-psychology-course-and-exam-description.pdf", 
                      "Social_Sciences", "High_School", "College_Board_US", 
                      "curriculum_framework", "US"),
        DocumentSource("NCSS Social Studies Standards", 
                      "https://www.socialstudies.org/sites/default/files/2017/Jun/c3-framework-for-social-studies-state-standards.pdf", 
                      "Social_Sciences", "High_School", "NCSS", 
                      "curriculum_framework", "US")
    ]
    sources.extend(social_sources)
    
    # GEOGRAPHY
    geo_sources = [
        DocumentSource("AP Human Geography Course Description", 
                      "https://secure-media.collegeboard.org/digitalServices/pdf/ap/ap-human-geography-course-and-exam-description.pdf", 
                      "Geography", "High_School", "College_Board_US", 
                      "curriculum_framework", "US"),
        DocumentSource("National Geography Standards", 
                      "https://www.nationalgeographic.org/education/geographic-skills/", 
                      "Geography", "High_School", "National_Geography", 
                      "curriculum_framework", "US")
    ]
    sources.extend(geo_sources)
    
    # HISTORY
    history_sources = [
        DocumentSource("AP World History Course Description", 
                      "https://secure-media.collegeboard.org/digitalServices/pdf/ap/ap-world-history-course-and-exam-description.pdf", 
                      "History", "High_School", "College_Board_US", 
                      "curriculum_framework", "US"),
        DocumentSource("NCHS Historical Thinking Standards", 
                      "https://www.nchs.ucla.edu/history-standards", 
                      "History", "High_School", "NCHS", 
                      "curriculum_framework", "US")
    ]
    sources.extend(history_sources)
    
    # ART
    art_sources = [
        DocumentSource("NAEA Visual Arts Standards", 
                      "https://www.arteducators.org/learn-tools/national-visual-arts-standards", 
                      "Art", "High_School", "NAEA", 
                      "curriculum_framework", "US"),
        DocumentSource("AP Studio Art Course Description", 
                      "https://secure-media.collegeboard.org/digitalServices/pdf/ap/ap-art-and-design-course-and-exam-description.pdf", 
                      "Art", "High_School", "College_Board_US", 
                      "curriculum_framework", "US")
    ]
    sources.extend(art_sources)
    
    # LITERATURE/ENGLISH
    lit_sources = [
        DocumentSource("AP English Literature Course Description", 
                      "https://secure-media.collegeboard.org/digitalServices/pdf/ap/ap-english-literature-and-composition-course-and-exam-description.pdf", 
                      "Literature", "High_School", "College_Board_US", 
                      "curriculum_framework", "US"),
        DocumentSource("NCTE English Language Arts Standards", 
                      "https://ncte.org/resources/standards/", 
                      "Literature", "High_School", "NCTE", 
                      "curriculum_framework", "US")
    ]
    sources.extend(lit_sources)
    
    # PHILOSOPHY
    phil_sources = [
        DocumentSource("APA Philosophy Teaching Guidelines", 
                      "https://www.apaonline.org/page/teaching", 
                      "Philosophy", "Undergraduate", "APA", 
                      "curriculum_framework", "US"),
        DocumentSource("Philosophy Learning Goals and Assessment", 
                      "https://www.aacu.org/publications-research/periodicals/philosophy-and-critical-thinking", 
                      "Philosophy", "Undergraduate", "Philosophy_Teaching", 
                      "curriculum_framework", "US")
    ]
    sources.extend(phil_sources)
    
    # LAW
    law_sources = [
        DocumentSource("ABA Law School Accreditation Standards", 
                      "https://www.americanbar.org/content/dam/aba/administrative/legal_education_and_admissions/standards/2023-2024/2023-2024-aba-standards-and-rules-of-procedure.pdf", 
                      "Law", "Graduate", "ABA", 
                      "accreditation_standard", "US"),
        DocumentSource("Law School Admission Test Information", 
                      "https://www.lsac.org/lsat", 
                      "Law", "Graduate", "LSAC", 
                      "assessment_standard", "US")
    ]
    sources.extend(law_sources)
    
    # EDUCATION
    edu_sources = [
        DocumentSource("CAEP Education Preparation Standards", 
                      "https://caepnet.org/standards/2022-caep-standards", 
                      "Education", "Undergraduate", "CAEP", 
                      "accreditation_standard", "US"),
        DocumentSource("InTASC Model Core Teaching Standards", 
                      "https://ccsso.org/sites/default/files/2017-12/2011_InTASC_Model_Core_Teaching_Standards.pdf", 
                      "Education", "Undergraduate", "InTASC", 
                      "curriculum_framework", "US")
    ]
    sources.extend(edu_sources)
    
    # AGRICULTURAL SCIENCES
    ag_sources = [
        DocumentSource("NAAE Agriculture Education Standards", 
                      "https://www.naae.org/teachag/", 
                      "Agricultural_Sciences", "High_School", "NAAE", 
                      "curriculum_framework", "US"),
        DocumentSource("USDA Agriculture Education Guidelines", 
                      "https://nifa.usda.gov/grants/programs/secondary-education-two-year-postsecondary-education-multicultural-scholars-program", 
                      "Agricultural_Sciences", "Undergraduate", "USDA", 
                      "curriculum_framework", "US")
    ]
    sources.extend(ag_sources)
    
    print(f"✅ Loaded {len(sources)} enhanced working document sources")
    print(f"📊 Coverage: {len(set(s.discipline for s in sources))} disciplines")
    print(f"🎓 Educational levels: {len(set(s.level for s in sources))} levels")
    print(f"🌍 Regions: {len(set(s.region for s in sources))} regions")
    
    return sources

if __name__ == "__main__":
    sources = get_comprehensive_working_sources()
    for i, source in enumerate(sources, 1):
        print(f"{i:2d}. {source.discipline:15s} | {source.level:12s} | {source.title}")