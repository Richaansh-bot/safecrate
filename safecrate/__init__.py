"""
Safecrate - Content Safety Validator for Indian Content Creators

Helps influencers validate their content before posting to ensure:
- Women's safety and dignity
- Cultural sensitivity
- Legal compliance (Indian laws)
- Community guidelines adherence
"""

__version__ = "0.1.0"
__author__ = "Safecrate Team"

from .analyzer import ContentAnalyzer, VideoMetadata
from .safety_checklist import WomenSafetyChecker, QuickSafetyQuiz
from .scorer import SensitivityScorer, QuickScorer
from .compliance import IndianLawChecker
from .reporter import SafetyReport

__all__ = [
    "ContentAnalyzer",
    "VideoMetadata",
    "WomenSafetyChecker",
    "QuickSafetyQuiz",
    "SensitivityScorer",
    "QuickScorer",
    "IndianLawChecker",
    "SafetyReport",
]
