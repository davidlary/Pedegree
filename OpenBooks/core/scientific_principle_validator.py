#!/usr/bin/env python3
"""
scientific_principle_validator.py - Validate discipline contexts against fundamental scientific principles

This module validates that discipline-specific contexts don't contradict fundamental
scientific principles, ensuring accuracy and consistency across the curriculum.
"""

import logging
import re
from typing import Dict, List, Optional, Set, Tuple
from dataclasses import dataclass
from enum import Enum

from .data_models import SubtopicEntry, ScientificViolation, AlertSeverity

logger = logging.getLogger(__name__)


class ViolationType(Enum):
    """Types of scientific principle violations."""
    CONTRADICTION = "Contradiction"
    INCONSISTENCY = "Inconsistency" 
    FACTUAL_ERROR = "Factual_Error"
    NOMENCLATURE_ERROR = "Nomenclature_Error"
    UNIT_ERROR = "Unit_Error"
    MAGNITUDE_ERROR = "Magnitude_Error"


@dataclass
class FundamentalPrinciple:
    """
    Goal: Represent a fundamental scientific principle for validation.
    
    Contains the principle statement, keywords for detection, and validation logic.
    """
    principle_id: str
    discipline: str
    principle_statement: str
    keywords: List[str]
    contradiction_patterns: List[str]  # Regex patterns that would violate this principle
    severity: AlertSeverity = AlertSeverity.HIGH
    
    def check_violation(self, text: str) -> Optional[str]:
        """Check if text violates this principle."""
        text_lower = text.lower()
        
        # Check for keyword presence first
        if not any(keyword.lower() in text_lower for keyword in self.keywords):
            return None
            
        # Check for contradiction patterns
        for pattern in self.contradiction_patterns:
            if re.search(pattern, text_lower, re.IGNORECASE):
                return f"Text contradicts {self.principle_statement}: matched pattern '{pattern}'"
        
        return None


class ScientificPrincipleValidator:
    """
    Goal: Validate discipline-specific contexts against fundamental scientific principles.
    
    Ensures that individual subtopic contexts don't contradict established scientific
    laws, principles, and nomenclature standards.
    """
    
    def __init__(self):
        self.fundamental_principles = self._load_fundamental_principles()
        self.nomenclature_standards = self._load_nomenclature_standards()
        self.unit_standards = self._load_unit_standards()
        self.magnitude_checks = self._load_magnitude_checks()
        
    def validate_scientific_consistency(self, curriculum: List[SubtopicEntry], 
                                      discipline: str) -> List[ScientificViolation]:
        """
        Goal: Validate entire curriculum against fundamental scientific principles.
        
        Checks each subtopic's discipline-specific context for violations of
        scientific principles, nomenclature, units, and reasonable magnitudes.
        """
        violations = []
        
        logger.info(f"Validating scientific consistency for {len(curriculum)} subtopics in {discipline}")
        
        for subtopic in curriculum:
            # Validate discipline-specific context
            context_violations = self._validate_context(subtopic, discipline)
            violations.extend(context_violations)
            
            # Validate learning objectives
            objective_violations = self._validate_learning_objectives(subtopic, discipline)
            violations.extend(objective_violations)
            
            # Validate key equations
            equation_violations = self._validate_equations(subtopic, discipline)
            violations.extend(equation_violations)
            
            # Validate experimental methods
            method_violations = self._validate_experimental_methods(subtopic, discipline)
            violations.extend(method_violations)
        
        logger.info(f"Found {len(violations)} scientific principle violations in {discipline}")
        return violations
    
    def validate_cross_disciplinary_consistency(self, contexts: Dict[str, str], 
                                              topic: str) -> List[ScientificViolation]:
        """
        Goal: Validate that different disciplinary contexts for same topic don't contradict.
        
        Ensures that the same concept described in different disciplines maintains
        scientific consistency while allowing discipline-specific emphasis.
        """
        violations = []
        disciplines = list(contexts.keys())
        
        # Compare each pair of disciplinary contexts
        for i, disc1 in enumerate(disciplines):
            for disc2 in disciplines[i+1:]:
                context1 = contexts[disc1]
                context2 = contexts[disc2]
                
                # Check for direct contradictions
                contradictions = self._find_contradictions(context1, context2, topic)
                for contradiction in contradictions:
                    violation = ScientificViolation(
                        subtopic_id=f"{topic}_{disc1}_{disc2}",
                        discipline=f"{disc1}|{disc2}",
                        violation_type=ViolationType.CONTRADICTION.value,
                        conflicting_principle=f"Cross-disciplinary consistency for {topic}",
                        description=contradiction,
                        severity=AlertSeverity.HIGH,
                        resolution_recommendation=f"Resolve contradiction between {disc1} and {disc2} contexts",
                        authoritative_sources=[],
                        confidence_score=0.8
                    )
                    violations.append(violation)
        
        return violations
    
    def _validate_context(self, subtopic: SubtopicEntry, discipline: str) -> List[ScientificViolation]:
        """Validate discipline-specific context against principles."""
        violations = []
        context = subtopic.discipline_specific_context
        
        if not context:
            return violations
        
        # Check against fundamental principles
        applicable_principles = [p for p in self.fundamental_principles 
                               if p.discipline == discipline or p.discipline == "universal"]
        
        for principle in applicable_principles:
            violation_msg = principle.check_violation(context)
            if violation_msg:
                violation = ScientificViolation(
                    subtopic_id=subtopic.id,
                    discipline=discipline,
                    violation_type=ViolationType.CONTRADICTION.value,
                    conflicting_principle=principle.principle_statement,
                    description=violation_msg,
                    severity=principle.severity,
                    resolution_recommendation=f"Revise context to align with {principle.principle_statement}",
                    authoritative_sources=[],
                    confidence_score=0.7
                )
                violations.append(violation)
        
        # Check nomenclature
        nomenclature_violations = self._check_nomenclature(context, discipline)
        for nom_violation in nomenclature_violations:
            violation = ScientificViolation(
                subtopic_id=subtopic.id,
                discipline=discipline,
                violation_type=ViolationType.NOMENCLATURE_ERROR.value,
                conflicting_principle="Standard scientific nomenclature",
                description=nom_violation,
                severity=AlertSeverity.MEDIUM,
                resolution_recommendation="Use standard scientific terminology",
                authoritative_sources=[],
                confidence_score=0.6
            )
            violations.append(violation)
        
        return violations
    
    def _validate_learning_objectives(self, subtopic: SubtopicEntry, 
                                    discipline: str) -> List[ScientificViolation]:
        """Validate discipline-specific learning objectives."""
        violations = []
        
        for objective in subtopic.discipline_specific_learning_objectives:
            # Check for scientifically impossible objectives
            if self._contains_impossible_claims(objective, discipline):
                violation = ScientificViolation(
                    subtopic_id=subtopic.id,
                    discipline=discipline,
                    violation_type=ViolationType.FACTUAL_ERROR.value,
                    conflicting_principle="Physical possibility",
                    description=f"Learning objective contains scientifically impossible claim: {objective}",
                    severity=AlertSeverity.HIGH,
                    resolution_recommendation="Revise objective to be scientifically accurate",
                    authoritative_sources=[],
                    confidence_score=0.8
                )
                violations.append(violation)
        
        return violations
    
    def _validate_equations(self, subtopic: SubtopicEntry, discipline: str) -> List[ScientificViolation]:
        """Validate key equations for dimensional analysis and correctness."""
        violations = []
        
        for equation in subtopic.key_equations:
            # Check dimensional analysis
            dimension_error = self._check_dimensional_analysis(equation, discipline)
            if dimension_error:
                violation = ScientificViolation(
                    subtopic_id=subtopic.id,
                    discipline=discipline,
                    violation_type=ViolationType.UNIT_ERROR.value,
                    conflicting_principle="Dimensional consistency",
                    description=f"Equation fails dimensional analysis: {equation} - {dimension_error}",
                    severity=AlertSeverity.HIGH,
                    resolution_recommendation="Correct equation to maintain dimensional consistency",
                    authoritative_sources=[],
                    confidence_score=0.9
                )
                violations.append(violation)
        
        return violations
    
    def _validate_experimental_methods(self, subtopic: SubtopicEntry, 
                                     discipline: str) -> List[ScientificViolation]:
        """Validate experimental methods for feasibility and safety."""
        violations = []
        
        for method in subtopic.experimental_methods:
            # Check for unsafe procedures
            safety_issues = self._check_experimental_safety(method, discipline)
            for issue in safety_issues:
                violation = ScientificViolation(
                    subtopic_id=subtopic.id,
                    discipline=discipline,
                    violation_type=ViolationType.FACTUAL_ERROR.value,
                    conflicting_principle="Laboratory safety standards",
                    description=f"Experimental method has safety concern: {issue}",
                    severity=AlertSeverity.CRITICAL,
                    resolution_recommendation="Revise method to ensure safety compliance",
                    authoritative_sources=[],
                    confidence_score=0.85
                )
                violations.append(violation)
        
        return violations
    
    def _load_fundamental_principles(self) -> List[FundamentalPrinciple]:
        """
        Goal: Load fundamental scientific principles for validation.
        
        Creates comprehensive list of scientific principles that discipline
        contexts must not contradict.
        """
        principles = []
        
        # Universal principles
        principles.extend([
            FundamentalPrinciple(
                principle_id="conservation_energy",
                discipline="universal",
                principle_statement="Conservation of Energy",
                keywords=["energy", "conservation", "total energy"],
                contradiction_patterns=[
                    r"energy.*created.*from.*nothing",
                    r"perpetual.*motion.*machine",
                    r"energy.*destroyed.*without.*conversion"
                ]
            ),
            FundamentalPrinciple(
                principle_id="conservation_mass",
                discipline="universal", 
                principle_statement="Conservation of Mass",
                keywords=["mass", "conservation", "chemical reaction"],
                contradiction_patterns=[
                    r"mass.*disappears.*chemical.*reaction",
                    r"atoms.*destroyed.*chemical.*process"
                ]
            )
        ])
        
        # Physics principles
        principles.extend([
            FundamentalPrinciple(
                principle_id="speed_of_light",
                discipline="Physics",
                principle_statement="Speed of light is the universal speed limit",
                keywords=["speed", "light", "velocity", "faster"],
                contradiction_patterns=[
                    r"faster.*than.*light.*possible",
                    r"exceed.*speed.*of.*light.*matter"
                ]
            ),
            FundamentalPrinciple(
                principle_id="thermodynamics_second",
                discipline="Physics",
                principle_statement="Second Law of Thermodynamics",
                keywords=["entropy", "thermodynamics", "heat", "efficiency"],
                contradiction_patterns=[
                    r"100%.*efficient.*heat.*engine",
                    r"entropy.*decreases.*isolated.*system"
                ]
            )
        ])
        
        # Chemistry principles
        principles.extend([
            FundamentalPrinciple(
                principle_id="atomic_theory",
                discipline="Chemistry",
                principle_statement="Atomic Theory",
                keywords=["atom", "element", "compound", "molecule"],
                contradiction_patterns=[
                    r"atoms.*indivisible.*modern.*sense",
                    r"elements.*change.*chemical.*reaction"
                ]
            ),
            FundamentalPrinciple(
                principle_id="periodic_trends",
                discipline="Chemistry",
                principle_statement="Periodic Table Trends",
                keywords=["periodic", "atomic", "radius", "electronegativity"],
                contradiction_patterns=[
                    r"atomic.*radius.*increases.*period",
                    r"electronegativity.*decreases.*group"
                ]
            )
        ])
        
        # Biology principles
        principles.extend([
            FundamentalPrinciple(
                principle_id="cell_theory",
                discipline="Biology",
                principle_statement="Cell Theory",
                keywords=["cell", "living", "organism", "life"],
                contradiction_patterns=[
                    r"spontaneous.*generation.*complex.*life",
                    r"living.*organisms.*without.*cells"
                ]
            ),
            FundamentalPrinciple(
                principle_id="evolution",
                discipline="Biology",
                principle_statement="Theory of Evolution",
                keywords=["evolution", "natural selection", "species", "adaptation"],
                contradiction_patterns=[
                    r"evolution.*goal.*directed.*process",
                    r"acquired.*characteristics.*inherited.*lamarck"
                ]
            )
        ])
        
        return principles
    
    def _load_nomenclature_standards(self) -> Dict[str, Dict[str, str]]:
        """Load standard scientific nomenclature by discipline."""
        return {
            "Chemistry": {
                "incorrect": ["sulfur dioxide", "sulfur trioxide"],
                "correct": ["sulphur dioxide", "sulphur trioxide"],
                "patterns": [
                    (r"\bsulfur\b", "sulphur"),  # IUPAC spelling
                ]
            },
            "Physics": {
                "incorrect": ["weight", "centrifugal force"],
                "correct": ["mass", "centripetal force"],
                "patterns": [
                    (r"\bweight\b(?!.*measurement)", "mass"),  # Weight vs mass
                ]
            },
            "Biology": {
                "incorrect": ["DNA replication", "RNA transcription"],
                "correct": ["DNA replication", "DNA transcription"],
                "patterns": []
            }
        }
    
    def _load_unit_standards(self) -> Dict[str, List[str]]:
        """Load standard units by discipline."""
        return {
            "Physics": ["m", "kg", "s", "A", "K", "mol", "cd", "N", "J", "W", "Pa"],
            "Chemistry": ["mol", "L", "atm", "K", "J", "cal", "M", "m", "g"],
            "Biology": ["g", "L", "mol", "°C", "pH", "bp", "Da", "kcal"]
        }
    
    def _load_magnitude_checks(self) -> Dict[str, Dict[str, Tuple[float, float]]]:
        """Load reasonable magnitude ranges for common quantities."""
        return {
            "Physics": {
                "speed_of_light": (2.99e8, 3.01e8),  # m/s
                "planck_constant": (6.62e-34, 6.63e-34),  # J⋅s
                "gravitational_acceleration": (9.7, 9.9)  # m/s²
            },
            "Chemistry": {
                "avogadro_number": (6.02e23, 6.03e23),
                "gas_constant": (8.31, 8.32),  # J/(mol⋅K)
                "room_temperature": (293, 298)  # K
            },
            "Biology": {
                "body_temperature": (310, 311),  # K
                "blood_ph": (7.35, 7.45),
                "cell_membrane_potential": (-90, -40)  # mV
            }
        }
    
    def _find_contradictions(self, context1: str, context2: str, topic: str) -> List[str]:
        """Find contradictions between two disciplinary contexts."""
        contradictions = []
        
        # Simple contradiction detection (can be enhanced)
        context1_lower = context1.lower()
        context2_lower = context2.lower()
        
        # Check for opposite statements
        contradiction_pairs = [
            ("increases", "decreases"),
            ("positive", "negative"), 
            ("linear", "nonlinear"),
            ("reversible", "irreversible"),
            ("stable", "unstable")
        ]
        
        for word1, word2 in contradiction_pairs:
            if word1 in context1_lower and word2 in context2_lower:
                if self._contexts_refer_to_same_property(context1, context2, word1, word2):
                    contradictions.append(f"Contradiction: {word1} vs {word2} for {topic}")
        
        return contradictions
    
    def _contexts_refer_to_same_property(self, context1: str, context2: str, 
                                       word1: str, word2: str) -> bool:
        """Check if contradictory words refer to the same property."""
        # Simple heuristic - check if surrounding words are similar
        # This is a simplified implementation that could be enhanced
        return True  # Conservative approach - flag potential contradictions
    
    def _contains_impossible_claims(self, objective: str, discipline: str) -> bool:
        """Check if learning objective contains scientifically impossible claims."""
        objective_lower = objective.lower()
        
        impossible_patterns = [
            r"exceed.*speed.*of.*light",
            r"100%.*efficient.*heat.*engine", 
            r"perpetual.*motion",
            r"create.*energy.*from.*nothing",
            r"violate.*conservation.*laws"
        ]
        
        return any(re.search(pattern, objective_lower) for pattern in impossible_patterns)
    
    def _check_dimensional_analysis(self, equation: str, discipline: str) -> Optional[str]:
        """Check equation for dimensional consistency."""
        # Simplified dimensional analysis
        # In a full implementation, this would parse equations and check units
        
        # Check for obvious unit mismatches
        unit_mismatches = [
            (r"kg.*\+.*m", "Cannot add mass and length"),
            (r"s.*\*.*kg.*=.*m", "Time × mass ≠ length"),
            (r"J.*\+.*N", "Cannot add energy and force")
        ]
        
        for pattern, error_msg in unit_mismatches:
            if re.search(pattern, equation, re.IGNORECASE):
                return error_msg
        
        return None
    
    def _check_experimental_safety(self, method: str, discipline: str) -> List[str]:
        """Check experimental method for safety concerns."""
        safety_issues = []
        method_lower = method.lower()
        
        # Check for dangerous procedures
        dangerous_patterns = [
            (r"mercury.*thermometer", "Mercury thermometers pose toxicity risk"),
            (r"open.*flame.*volatile.*solvent", "Open flames with volatile solvents create fire hazard"),
            (r"concentrated.*acid.*base.*mixing", "Mixing concentrated acids and bases creates heat/splash hazard"),
            (r"radioactive.*material.*without.*protection", "Radioactive materials require proper shielding")
        ]
        
        for pattern, issue in dangerous_patterns:
            if re.search(pattern, method_lower):
                safety_issues.append(issue)
        
        return safety_issues
    
    def _check_nomenclature(self, text: str, discipline: str) -> List[str]:
        """Check text for nomenclature violations."""
        violations = []
        
        if discipline not in self.nomenclature_standards:
            return violations
        
        standards = self.nomenclature_standards[discipline]
        text_lower = text.lower()
        
        # Check for incorrect terms
        for incorrect_term in standards.get("incorrect", []):
            if incorrect_term.lower() in text_lower:
                violations.append(f"Use of non-standard term: {incorrect_term}")
        
        # Check patterns
        for pattern, replacement in standards.get("patterns", []):
            if re.search(pattern, text, re.IGNORECASE):
                violations.append(f"Non-standard usage detected: pattern '{pattern}' should be '{replacement}'")
        
        return violations