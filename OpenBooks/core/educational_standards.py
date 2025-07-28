"""
core/educational_standards.py - Educational Standards and Assessment Manager

Goal: Provide comprehensive management of educational standards, exam requirements,
prerequisite relationships, and curriculum categorization based on domain expertise.

This module encapsulates domain knowledge about educational standards, professional
examinations, and pedagogical relationships across academic disciplines.
"""

import re
from typing import Dict, List, Set, Optional, Any
from collections import defaultdict


class EducationalStandardsManager:
    """
    Manages educational standards, exam requirements, and prerequisite relationships
    across academic disciplines using comprehensive domain knowledge.
    
    This class serves as the authoritative source for:
    - Professional and academic examination standards
    - Prerequisite relationships between concepts
    - Curriculum categorization and organization
    - Educational level progressions
    """
    
    def __init__(self):
        """Initialize the standards manager with comprehensive domain knowledge."""
        
        # Exam standards by discipline (based on comprehensive surveys)
        self._exam_standards = self._initialize_exam_standards()
        
        # Prerequisite rules by discipline (educational domain knowledge)
        self._prerequisite_rules = self._initialize_prerequisite_rules()
        
        # Essential concepts by discipline (domain expertise)
        self._essential_concepts = self._initialize_essential_concepts()
        
        # Category classification patterns
        self._category_patterns = self._initialize_category_patterns()
    
    def get_exam_standards(self, discipline: str) -> Set[str]:
        """Get relevant exam standards for a discipline."""
        return self._exam_standards.get(discipline, set())
    
    def get_prerequisite_rules(self, discipline: str) -> Dict[str, List[str]]:
        """Get prerequisite rules for a discipline."""
        return self._prerequisite_rules.get(discipline, {})
    
    def get_essential_concepts(self, discipline: str) -> Dict[str, List[Dict[str, Any]]]:
        """Get essential concepts for a discipline."""
        return self._essential_concepts.get(discipline, {})
    
    def categorize_concept(self, discipline: str, title: str) -> str:
        """Categorize a concept based on discipline and title."""
        
        title_lower = title.lower()
        patterns = self._category_patterns.get(discipline, {})
        
        # Check for category-specific keywords
        for category, keywords in patterns.items():
            if any(keyword in title_lower for keyword in keywords):
                return category
        
        # Default category
        return f'General {discipline}'
    
    def _initialize_exam_standards(self) -> Dict[str, Set[str]]:
        """Initialize comprehensive exam standards mapping."""
        return {
            'Physics': {
                'AP-Physics', 'SAT-Physics', 'GRE-Physics', 'MCAT-Physics',
                'IB-Physics', 'A-Level-Physics', 'PGRE', 'USAPHO'
            },
            'Biology': {
                'AP-Biology', 'SAT-Biology', 'MCAT-Biology', 'GRE-Biology',
                'IB-Biology', 'A-Level-Biology', 'USABO', 'NATS'
            },
            'Chemistry': {
                'AP-Chemistry', 'SAT-Chemistry', 'MCAT-Chemistry', 'GRE-Chemistry',
                'IB-Chemistry', 'A-Level-Chemistry', 'USNCO', 'IChO'
            },
            'Mathematics': {
                'AP-Calculus', 'AP-Statistics', 'SAT-Math', 'GRE-Math',
                'IB-Mathematics', 'A-Level-Mathematics', 'AMC', 'AIME', 'USAMO',
                'Putnam', 'IMO'
            },
            'Economics': {
                'AP-Economics', 'GRE-Economics', 'CFA', 'FRM', 
                'IB-Economics', 'A-Level-Economics', 'CAIA'
            },
            'Psychology': {
                'AP-Psychology', 'GRE-Psychology', 'EPPP', 'IB-Psychology',
                'PRAXIS'
            },
            'Business': {
                'CPA', 'CFA', 'FRM', 'GMAT', 'Series-7', 'Series-63', 'PMP',
                'CIA', 'CMA', 'CISA'
            },
            'Medicine': {
                'MCAT', 'USMLE', 'COMLEX', 'PCAT', 'DAT', 'OAT', 'NBME'
            },
            'Law': {
                'LSAT', 'Bar-Exam', 'MPRE', 'UBE'
            },
            'Computer Science': {
                'AP-Computer-Science', 'GRE-Computer-Science', 'CompTIA', 'CISSP',
                'AWS-Certification', 'Microsoft-Certification', 'Cisco-Certification'
            },
            'Engineering': {
                'FE-Exam', 'PE-Exam', 'GRE-Engineering', 'ABET'
            },
            'Art': {
                'AP-Art', 'IB-Visual-Arts', 'Portfolio-Review'
            },
            'History': {
                'AP-History', 'SAT-History', 'IB-History', 'A-Level-History'
            },
            'Political Science': {
                'AP-Government', 'GRE-Political-Science', 'LSAT', 'Foreign-Service'
            },
            'Sociology': {
                'AP-Psychology', 'GRE-Sociology', 'MSW-Exam'
            }
        }
    
    def _initialize_prerequisite_rules(self) -> Dict[str, Dict[str, List[str]]]:
        """Initialize prerequisite rules based on educational domain knowledge."""
        return {
            'Physics': {
                'Classical Mechanics': [],
                'Thermodynamics': ['Classical Mechanics'],
                'Electromagnetism': ['Classical Mechanics', 'Vector Calculus'],
                'Quantum Mechanics': ['Classical Mechanics', 'Electromagnetism', 'Linear Algebra'],
                'Statistical Mechanics': ['Thermodynamics', 'Quantum Mechanics'],
                'Relativity': ['Classical Mechanics', 'Electromagnetism'],
                'Optics and Waves': ['Electromagnetism', 'Wave Physics'],
                'Nuclear Physics': ['Quantum Mechanics', 'Atomic Physics'],
                'Particle Physics': ['Quantum Mechanics', 'Nuclear Physics', 'Relativity'],
                'Condensed Matter': ['Quantum Mechanics', 'Statistical Mechanics'],
                'Astrophysics': ['Classical Mechanics', 'Electromagnetism', 'Thermodynamics'],
                'Biophysics': ['Classical Mechanics', 'Thermodynamics', 'Biology Fundamentals'],
                'Computational Physics': ['Classical Mechanics', 'Programming Fundamentals'],
                'Fluid Dynamics': ['Classical Mechanics', 'Partial Differential Equations'],
                'Plasma Physics': ['Electromagnetism', 'Statistical Mechanics']
            },
            'Mathematics': {
                'Algebra': [],
                'Geometry': ['Algebra'],
                'Trigonometry': ['Algebra', 'Geometry'],
                'Precalculus': ['Algebra', 'Trigonometry'],
                'Calculus I': ['Precalculus'],
                'Calculus II': ['Calculus I'],
                'Calculus III': ['Calculus II'],
                'Linear Algebra': ['Calculus I'],
                'Differential Equations': ['Calculus II', 'Linear Algebra'],
                'Real Analysis': ['Calculus III', 'Linear Algebra'],
                'Complex Analysis': ['Real Analysis'],
                'Abstract Algebra': ['Linear Algebra'],
                'Topology': ['Real Analysis'],
                'Statistics': ['Calculus I'],
                'Probability': ['Calculus II'],
                'Number Theory': ['Abstract Algebra'],
                'Discrete Mathematics': ['Algebra'],
                'Numerical Analysis': ['Linear Algebra', 'Programming']
            },
            'Chemistry': {
                'General Chemistry': [],
                'Organic Chemistry': ['General Chemistry'],
                'Physical Chemistry': ['General Chemistry', 'Calculus', 'Physics'],
                'Analytical Chemistry': ['General Chemistry'],
                'Inorganic Chemistry': ['General Chemistry'],
                'Biochemistry': ['Organic Chemistry', 'Biology'],
                'Quantum Chemistry': ['Physical Chemistry', 'Quantum Mechanics'],
                'Materials Chemistry': ['Physical Chemistry', 'Inorganic Chemistry'],
                'Environmental Chemistry': ['General Chemistry', 'Environmental Science'],
                'Medicinal Chemistry': ['Organic Chemistry', 'Biochemistry'],
                'Polymer Chemistry': ['Organic Chemistry', 'Physical Chemistry'],
                'Spectroscopy': ['Physical Chemistry', 'Quantum Chemistry']
            },
            'Biology': {
                'Cell Biology': [],
                'Molecular Biology': ['Cell Biology'],
                'Genetics': ['Cell Biology', 'Molecular Biology'],
                'Evolution': ['Genetics'],
                'Ecology': ['Evolution'],
                'Physiology': ['Cell Biology'],
                'Anatomy': ['Cell Biology'],
                'Biochemistry': ['Molecular Biology', 'Chemistry'],
                'Microbiology': ['Cell Biology', 'Molecular Biology'],
                'Neuroscience': ['Physiology', 'Anatomy'],
                'Developmental Biology': ['Molecular Biology', 'Genetics'],
                'Bioinformatics': ['Molecular Biology', 'Computer Science'],
                'Immunology': ['Cell Biology', 'Biochemistry'],
                'Pharmacology': ['Biochemistry', 'Physiology'],
                'Marine Biology': ['Cell Biology', 'Ecology'],
                'Conservation Biology': ['Ecology', 'Genetics']
            },
            'Computer Science': {
                'Programming Fundamentals': [],
                'Data Structures': ['Programming Fundamentals'],
                'Algorithms': ['Data Structures'],
                'Computer Architecture': ['Programming Fundamentals'],
                'Operating Systems': ['Computer Architecture', 'Data Structures'],
                'Database Systems': ['Data Structures'],
                'Software Engineering': ['Data Structures', 'Algorithms'],
                'Computer Networks': ['Operating Systems'],
                'Cybersecurity': ['Computer Networks', 'Operating Systems'],
                'Artificial Intelligence': ['Algorithms', 'Statistics'],
                'Machine Learning': ['Artificial Intelligence', 'Linear Algebra'],
                'Computer Graphics': ['Linear Algebra', 'Algorithms'],
                'Distributed Systems': ['Operating Systems', 'Computer Networks'],
                'Theory of Computation': ['Algorithms', 'Discrete Mathematics']
            },
            'Economics': {
                'Microeconomics': [],
                'Macroeconomics': ['Microeconomics'],
                'Econometrics': ['Statistics', 'Microeconomics'],
                'International Economics': ['Macroeconomics'],
                'Public Economics': ['Microeconomics', 'Macroeconomics'],
                'Labor Economics': ['Microeconomics'],
                'Industrial Organization': ['Microeconomics'],
                'Development Economics': ['Macroeconomics'],
                'Financial Economics': ['Macroeconomics'],
                'Behavioral Economics': ['Microeconomics', 'Psychology'],
                'Game Theory': ['Microeconomics', 'Mathematics'],
                'Environmental Economics': ['Microeconomics', 'Environmental Science']
            }
        }
    
    def _initialize_essential_concepts(self) -> Dict[str, Dict[str, List[Dict[str, Any]]]]:
        """Initialize essential concepts by discipline and category."""
        return {
            'Physics': {
                'Classical Mechanics': [
                    {'title': 'Newton\'s Laws of Motion', 'description': 'Fundamental laws governing motion', 'level': 'HS-Found', 'difficulty': 3.0, 'hours': 2.0},
                    {'title': 'Conservation of Energy', 'description': 'Energy conservation principle', 'level': 'HS-Found', 'difficulty': 4.0, 'hours': 2.0},
                    {'title': 'Conservation of Momentum', 'description': 'Momentum conservation in collisions', 'level': 'HS-Adv', 'difficulty': 5.0, 'hours': 2.0},
                    {'title': 'Rotational Dynamics', 'description': 'Motion of rotating objects', 'level': 'UG-Intro', 'difficulty': 6.0, 'hours': 3.0},
                    {'title': 'Oscillatory Motion', 'description': 'Simple harmonic motion and vibrations', 'level': 'UG-Intro', 'difficulty': 5.0, 'hours': 2.0},
                    {'title': 'Lagrangian Mechanics', 'description': 'Advanced formulation of mechanics', 'level': 'UG-Adv', 'difficulty': 8.0, 'hours': 4.0},
                    {'title': 'Hamiltonian Mechanics', 'description': 'Phase space formulation', 'level': 'Grad-Intro', 'difficulty': 9.0, 'hours': 5.0},
                    {'title': 'Chaos Theory', 'description': 'Nonlinear dynamics and chaos', 'level': 'Grad-Adv', 'difficulty': 9.0, 'hours': 4.0}
                ],
                'Thermodynamics': [
                    {'title': 'Temperature and Heat', 'description': 'Basic thermal concepts', 'level': 'HS-Found', 'difficulty': 2.0, 'hours': 1.5},
                    {'title': 'First Law of Thermodynamics', 'description': 'Energy conservation in thermal systems', 'level': 'HS-Adv', 'difficulty': 4.0, 'hours': 2.0},
                    {'title': 'Second Law of Thermodynamics', 'description': 'Entropy and irreversibility', 'level': 'HS-Adv', 'difficulty': 6.0, 'hours': 3.0},
                    {'title': 'Heat Engines', 'description': 'Conversion of heat to work', 'level': 'UG-Intro', 'difficulty': 6.0, 'hours': 2.0},
                    {'title': 'Phase Transitions', 'description': 'Changes of state in matter', 'level': 'UG-Intro', 'difficulty': 5.0, 'hours': 2.0},
                    {'title': 'Statistical Mechanics', 'description': 'Microscopic origin of thermodynamics', 'level': 'UG-Adv', 'difficulty': 8.0, 'hours': 4.0},
                    {'title': 'Critical Phenomena', 'description': 'Behavior near phase transitions', 'level': 'Grad-Intro', 'difficulty': 8.5, 'hours': 3.0}
                ],
                'Electromagnetism': [
                    {'title': 'Electric Charge and Force', 'description': 'Fundamental electric interactions', 'level': 'HS-Found', 'difficulty': 2.0, 'hours': 1.5},
                    {'title': 'Coulomb\'s Law', 'description': 'Electric force between charges', 'level': 'HS-Found', 'difficulty': 3.0, 'hours': 2.0},
                    {'title': 'Electric Fields and Potential', 'description': 'Electric field concepts', 'level': 'HS-Adv', 'difficulty': 5.0, 'hours': 3.0},
                    {'title': 'Magnetic Fields', 'description': 'Magnetic force and field', 'level': 'HS-Adv', 'difficulty': 5.0, 'hours': 3.0},
                    {'title': 'Electromagnetic Induction', 'description': 'Faraday\'s law and Lenz\'s law', 'level': 'UG-Intro', 'difficulty': 6.0, 'hours': 3.0},
                    {'title': 'Maxwell\'s Equations', 'description': 'Fundamental equations of electromagnetism', 'level': 'UG-Intro', 'difficulty': 7.0, 'hours': 4.0},
                    {'title': 'Electromagnetic Waves', 'description': 'Wave solutions to Maxwell equations', 'level': 'UG-Adv', 'difficulty': 7.0, 'hours': 3.0},
                    {'title': 'Gauge Theory', 'description': 'Advanced electromagnetic theory', 'level': 'Grad-Intro', 'difficulty': 9.0, 'hours': 5.0}
                ],
                'Quantum Mechanics': [
                    {'title': 'Photoelectric Effect', 'description': 'Quantum nature of light', 'level': 'HS-Adv', 'difficulty': 5.0, 'hours': 2.0},
                    {'title': 'Wave-Particle Duality', 'description': 'Dual nature of matter and light', 'level': 'HS-Adv', 'difficulty': 6.0, 'hours': 2.0},
                    {'title': 'Uncertainty Principle', 'description': 'Heisenberg uncertainty relations', 'level': 'UG-Intro', 'difficulty': 6.0, 'hours': 2.0},
                    {'title': 'Schrödinger Equation', 'description': 'Fundamental equation of quantum mechanics', 'level': 'UG-Intro', 'difficulty': 8.0, 'hours': 4.0},
                    {'title': 'Quantum Harmonic Oscillator', 'description': 'Fundamental quantum system', 'level': 'UG-Adv', 'difficulty': 7.0, 'hours': 3.0},
                    {'title': 'Hydrogen Atom', 'description': 'Exact solution for hydrogen', 'level': 'UG-Adv', 'difficulty': 8.0, 'hours': 4.0},
                    {'title': 'Angular Momentum', 'description': 'Quantum angular momentum theory', 'level': 'UG-Adv', 'difficulty': 8.0, 'hours': 4.0},
                    {'title': 'Quantum Entanglement', 'description': 'Non-local quantum correlations', 'level': 'Grad-Intro', 'difficulty': 8.0, 'hours': 3.0},
                    {'title': 'Quantum Field Theory', 'description': 'Relativistic quantum mechanics', 'level': 'Grad-Adv', 'difficulty': 10.0, 'hours': 6.0}
                ],
                'Optics and Waves': [
                    {'title': 'Geometric Optics', 'description': 'Ray optics and imaging', 'level': 'HS-Found', 'difficulty': 3.0, 'hours': 2.0},
                    {'title': 'Wave Properties of Light', 'description': 'Basic wave phenomena', 'level': 'HS-Adv', 'difficulty': 4.0, 'hours': 2.0},
                    {'title': 'Interference', 'description': 'Wave interference patterns', 'level': 'HS-Adv', 'difficulty': 5.0, 'hours': 2.5},
                    {'title': 'Diffraction', 'description': 'Wave diffraction phenomena', 'level': 'UG-Intro', 'difficulty': 6.0, 'hours': 3.0},
                    {'title': 'Polarization', 'description': 'Polarized light and optics', 'level': 'UG-Intro', 'difficulty': 5.0, 'hours': 2.0},
                    {'title': 'Fourier Optics', 'description': 'Frequency domain optics', 'level': 'UG-Adv', 'difficulty': 7.0, 'hours': 3.0},
                    {'title': 'Nonlinear Optics', 'description': 'High intensity optical phenomena', 'level': 'Grad-Intro', 'difficulty': 8.0, 'hours': 4.0}
                ],
                'Nuclear Physics': [
                    {'title': 'Nuclear Structure', 'description': 'Structure of atomic nuclei', 'level': 'UG-Intro', 'difficulty': 6.0, 'hours': 3.0},
                    {'title': 'Radioactive Decay', 'description': 'Nuclear decay processes', 'level': 'HS-Adv', 'difficulty': 4.0, 'hours': 2.0},
                    {'title': 'Nuclear Reactions', 'description': 'Fusion, fission, and reactions', 'level': 'UG-Adv', 'difficulty': 7.0, 'hours': 3.0},
                    {'title': 'Nuclear Models', 'description': 'Shell model and collective model', 'level': 'Grad-Intro', 'difficulty': 8.0, 'hours': 4.0}
                ],
                'Particle Physics': [
                    {'title': 'Elementary Particles', 'description': 'Fundamental particles and forces', 'level': 'UG-Intro', 'difficulty': 6.0, 'hours': 2.0},
                    {'title': 'Standard Model', 'description': 'Theory of fundamental particles', 'level': 'UG-Adv', 'difficulty': 8.0, 'hours': 4.0},
                    {'title': 'Feynman Diagrams', 'description': 'Particle interaction calculations', 'level': 'Grad-Intro', 'difficulty': 9.0, 'hours': 5.0},
                    {'title': 'Symmetries and Conservation', 'description': 'Fundamental symmetries in physics', 'level': 'Grad-Adv', 'difficulty': 9.0, 'hours': 4.0}
                ],
                'Astrophysics': [
                    {'title': 'Stellar Properties', 'description': 'Basic properties of stars', 'level': 'HS-Adv', 'difficulty': 4.0, 'hours': 2.0},
                    {'title': 'Stellar Evolution', 'description': 'Life cycle of stars', 'level': 'UG-Intro', 'difficulty': 5.0, 'hours': 3.0},
                    {'title': 'Galaxies', 'description': 'Structure and evolution of galaxies', 'level': 'UG-Intro', 'difficulty': 5.0, 'hours': 2.0},
                    {'title': 'Cosmology', 'description': 'Origin and evolution of universe', 'level': 'UG-Adv', 'difficulty': 7.0, 'hours': 4.0},
                    {'title': 'Black Holes', 'description': 'Physics of black holes', 'level': 'Grad-Intro', 'difficulty': 8.0, 'hours': 3.0}
                ],
                'Condensed Matter': [
                    {'title': 'Crystal Structure', 'description': 'Structure of crystalline solids', 'level': 'UG-Intro', 'difficulty': 5.0, 'hours': 2.0},
                    {'title': 'Electronic Properties', 'description': 'Electronic behavior in solids', 'level': 'UG-Adv', 'difficulty': 7.0, 'hours': 4.0},
                    {'title': 'Magnetism', 'description': 'Magnetic properties of materials', 'level': 'UG-Adv', 'difficulty': 6.0, 'hours': 3.0},
                    {'title': 'Superconductivity', 'description': 'Zero resistance phenomena', 'level': 'Grad-Intro', 'difficulty': 8.0, 'hours': 4.0}
                ]
            },
            # Add essential concepts for other disciplines as needed
            'Mathematics': {
                'Algebra': [
                    {'title': 'Linear Equations', 'description': 'Solving linear equations', 'level': 'HS-Found', 'difficulty': 2.0, 'hours': 1.0},
                    {'title': 'Quadratic Equations', 'description': 'Solving quadratic equations', 'level': 'HS-Found', 'difficulty': 3.0, 'hours': 1.5},
                    {'title': 'Polynomial Functions', 'description': 'Properties of polynomials', 'level': 'HS-Adv', 'difficulty': 4.0, 'hours': 2.0}
                ],
                'Calculus I': [
                    {'title': 'Limits', 'description': 'Concept of limits', 'level': 'UG-Intro', 'difficulty': 5.0, 'hours': 3.0},
                    {'title': 'Derivatives', 'description': 'Differentiation and applications', 'level': 'UG-Intro', 'difficulty': 6.0, 'hours': 4.0},
                    {'title': 'Integrals', 'description': 'Integration and applications', 'level': 'UG-Intro', 'difficulty': 6.0, 'hours': 4.0}
                ]
            }
        }
    
    def _initialize_category_patterns(self) -> Dict[str, Dict[str, List[str]]]:
        """Initialize category classification patterns."""
        return {
            'Physics': {
                'Classical Mechanics': [
                    'newton', 'force', 'motion', 'momentum', 'energy', 'mechanics', 'dynamics',
                    'kinematics', 'collision', 'rotation', 'oscillation', 'harmonic', 'pendulum',
                    'projectile', 'friction', 'gravity', 'lagrangian', 'hamiltonian'
                ],
                'Thermodynamics': [
                    'thermodynamic', 'heat', 'temperature', 'entropy', 'thermal', 'engine',
                    'refrigerator', 'carnot', 'phase', 'pressure', 'volume', 'gas', 'steam',
                    'calorimetry', 'specific heat', 'latent heat'
                ],
                'Electromagnetism': [
                    'electric', 'magnetic', 'electromagnetic', 'current', 'voltage', 'charge',
                    'field', 'potential', 'capacitor', 'inductor', 'circuit', 'ohm', 'faraday',
                    'maxwell', 'gauss', 'ampere', 'coulomb', 'induction'
                ],
                'Quantum Mechanics': [
                    'quantum', 'wave function', 'schrodinger', 'heisenberg', 'uncertainty',
                    'particle', 'photon', 'electron', 'orbital', 'spin', 'entanglement',
                    'superposition', 'measurement', 'operator', 'eigenvalue'
                ],
                'Optics and Waves': [
                    'wave', 'optic', 'light', 'laser', 'interference', 'diffraction',
                    'polarization', 'refraction', 'reflection', 'lens', 'mirror',
                    'spectrum', 'wavelength', 'frequency', 'electromagnetic radiation'
                ],
                'Nuclear Physics': [
                    'nuclear', 'radioactive', 'decay', 'fission', 'fusion', 'isotope',
                    'nucleus', 'proton', 'neutron', 'alpha', 'beta', 'gamma',
                    'half-life', 'radiation', 'reactor'
                ],
                'Relativity': [
                    'relativity', 'einstein', 'spacetime', 'lorentz', 'time dilation',
                    'length contraction', 'mass-energy', 'four-vector', 'minkowski',
                    'general relativity', 'curvature', 'geodesic'
                ],
                'Particle Physics': [
                    'particle', 'quark', 'lepton', 'boson', 'fermion', 'standard model',
                    'feynman', 'gauge', 'symmetry', 'higgs', 'neutrino', 'muon',
                    'accelerator', 'collider', 'antimatter'
                ],
                'Astrophysics': [
                    'astro', 'stellar', 'galaxy', 'cosmic', 'universe', 'cosmology',
                    'black hole', 'neutron star', 'supernova', 'redshift', 'hubble',
                    'dark matter', 'dark energy', 'big bang'
                ],
                'Condensed Matter': [
                    'solid state', 'crystal', 'lattice', 'conductor', 'semiconductor',
                    'insulator', 'superconductor', 'band', 'phonon', 'fermi',
                    'magnetic material', 'phase transition'
                ]
            },
            'Mathematics': {
                'Algebra': [
                    'equation', 'polynomial', 'linear', 'quadratic', 'variable',
                    'coefficient', 'root', 'factor', 'expression', 'inequality'
                ],
                'Geometry': [
                    'triangle', 'circle', 'polygon', 'angle', 'area', 'volume',
                    'theorem', 'proof', 'congruent', 'similar', 'coordinate'
                ],
                'Calculus': [
                    'limit', 'derivative', 'integral', 'continuity', 'differentiation',
                    'integration', 'series', 'convergence', 'taylor', 'optimization'
                ],
                'Linear Algebra': [
                    'matrix', 'vector', 'eigenvalue', 'eigenvector', 'determinant',
                    'linear transformation', 'basis', 'dimension', 'rank', 'span'
                ],
                'Statistics': [
                    'probability', 'distribution', 'mean', 'variance', 'correlation',
                    'regression', 'hypothesis', 'confidence', 'sample', 'population'
                ]
            },
            'Chemistry': {
                'General Chemistry': [
                    'atom', 'molecule', 'element', 'compound', 'periodic table',
                    'bond', 'reaction', 'stoichiometry', 'mole', 'molarity'
                ],
                'Organic Chemistry': [
                    'carbon', 'hydrocarbon', 'functional group', 'isomer', 'synthesis',
                    'mechanism', 'stereochemistry', 'aromatic', 'alkyl', 'carbonyl'
                ],
                'Physical Chemistry': [
                    'thermodynamics', 'kinetics', 'equilibrium', 'phase diagram',
                    'spectroscopy', 'quantum chemistry', 'molecular orbital'
                ],
                'Analytical Chemistry': [
                    'titration', 'chromatography', 'spectroscopy', 'electrochemistry',
                    'mass spectrometry', 'separation', 'quantitative analysis'
                ],
                'Biochemistry': [
                    'enzyme', 'protein', 'dna', 'rna', 'metabolism', 'glycolysis',
                    'amino acid', 'nucleotide', 'cellular respiration'
                ]
            },
            'Biology': {
                'Cell Biology': [
                    'cell', 'membrane', 'organelle', 'nucleus', 'mitochondria',
                    'chloroplast', 'cytoplasm', 'cellular', 'division', 'cycle'
                ],
                'Molecular Biology': [
                    'dna', 'rna', 'protein', 'gene', 'transcription', 'translation',
                    'replication', 'mutation', 'molecular', 'genetic code'
                ],
                'Genetics': [
                    'inheritance', 'allele', 'chromosome', 'mendel', 'punnett',
                    'dominant', 'recessive', 'genotype', 'phenotype', 'linkage'
                ],
                'Evolution': [
                    'natural selection', 'darwin', 'adaptation', 'species',
                    'fossil', 'phylogeny', 'mutation', 'genetic drift'
                ],
                'Ecology': [
                    'ecosystem', 'population', 'community', 'food chain',
                    'biodiversity', 'conservation', 'environmental', 'habitat'
                ]
            }
        }
    
    def detect_exam_alignment(self, discipline: str, concepts: List[str]) -> Dict[str, float]:
        """
        Detect which exams a curriculum aligns with based on concept coverage.
        
        Args:
            discipline: Academic discipline
            concepts: List of concept titles in curriculum
        
        Returns:
            Dictionary mapping exam names to alignment scores (0-1)
        """
        
        exam_standards = self.get_exam_standards(discipline)
        if not exam_standards:
            return {}
        
        # Create concept coverage analysis
        concept_text = ' '.join(concepts).lower()
        
        # Define exam-specific keywords (simplified example)
        exam_keywords = {
            'AP-Physics': ['mechanics', 'electricity', 'magnetism', 'waves', 'modern physics'],
            'MCAT-Physics': ['kinematics', 'dynamics', 'energy', 'thermodynamics', 'waves', 'atomic'],
            'GRE-Physics': ['classical mechanics', 'electromagnetism', 'quantum', 'thermodynamics', 'laboratory'],
            # Add more exam-specific patterns as needed
        }
        
        alignment_scores = {}
        for exam in exam_standards:
            if exam in exam_keywords:
                keywords = exam_keywords[exam]
                matches = sum(1 for keyword in keywords if keyword in concept_text)
                alignment_scores[exam] = matches / len(keywords)
        
        return alignment_scores
    
    def suggest_missing_concepts(self, discipline: str, current_concepts: List[str]) -> List[Dict[str, Any]]:
        """
        Suggest concepts that might be missing from a curriculum.
        
        Args:
            discipline: Academic discipline
            current_concepts: List of current concept titles
        
        Returns:
            List of suggested concepts with metadata
        """
        
        essential_concepts = self.get_essential_concepts(discipline)
        current_titles = {title.lower() for title in current_concepts}
        
        suggestions = []
        for category, concept_list in essential_concepts.items():
            for concept_info in concept_list:
                if concept_info['title'].lower() not in current_titles:
                    suggestions.append({
                        'title': concept_info['title'],
                        'category': category,
                        'level': concept_info['level'],
                        'difficulty': concept_info['difficulty'],
                        'hours': concept_info['hours'],
                        'importance': 'high' if concept_info['difficulty'] >= 7.0 else 'medium'
                    })
        
        # Sort by importance and difficulty
        suggestions.sort(key=lambda x: (x['importance'] == 'high', x['difficulty']), reverse=True)
        
        return suggestions[:20]  # Return top 20 suggestions
    
    def validate_prerequisite_chain(self, discipline: str, concept_sequence: List[str]) -> Dict[str, Any]:
        """
        Validate that a sequence of concepts follows proper prerequisite ordering.
        
        Args:
            discipline: Academic discipline
            concept_sequence: Ordered list of concept titles
        
        Returns:
            Validation results with violations and suggestions
        """
        
        prereq_rules = self.get_prerequisite_rules(discipline)
        validation = {
            'is_valid': True,
            'violations': [],
            'suggestions': []
        }
        
        # Simple validation: check if advanced topics come before basics
        basic_keywords = ['introduction', 'basic', 'fundamental', 'elementary']
        advanced_keywords = ['advanced', 'quantum', 'relativistic', 'nonlinear']
        
        for i, concept in enumerate(concept_sequence):
            concept_lower = concept.lower()
            
            # Check if advanced concept appears too early
            if any(keyword in concept_lower for keyword in advanced_keywords):
                # Look for basic concepts that should come first
                for j in range(i + 1, len(concept_sequence)):
                    later_concept = concept_sequence[j].lower()
                    if any(keyword in later_concept for keyword in basic_keywords):
                        validation['violations'].append({
                            'type': 'prerequisite_violation',
                            'advanced_concept': concept,
                            'basic_concept': concept_sequence[j],
                            'suggestion': f'Consider moving "{concept_sequence[j]}" before "{concept}"'
                        })
                        validation['is_valid'] = False
        
        return validation