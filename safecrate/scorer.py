"""
Sensitivity Scoring Engine
Calculates overall content safety scores and risk levels
"""

from dataclasses import dataclass
from typing import Dict, List
import json


@dataclass
class RiskScore:
    category: str
    score: float
    risk_level: str
    color: str

    def to_dict(self) -> Dict:
        return {
            "category": self.category,
            "score": self.score,
            "risk_level": self.risk_level,
            "color": self.color,
        }


class SensitivityScorer:
    """
    Calculates comprehensive sensitivity scores for content.
    Weighted scoring based on Indian context and women's safety.
    """

    # Category weights (higher = more important)
    WEIGHTS = {
        "women_safety": 0.25,  # Highest priority
        "privacy": 0.18,
        "violence": 0.15,
        "sexual_content": 0.15,
        "harassment": 0.12,
        "legal": 0.10,
        "cultural_sensitivity": 0.08,
        "self_harm": 0.08,
        "dangerous_activities": 0.07,
        "misinformation": 0.05,
    }

    # Colors for different risk levels
    COLORS = {
        "safe": "#22c55e",  # Green
        "low": "#84cc16",  # Lime
        "medium": "#eab308",  # Yellow
        "high": "#f97316",  # Orange
        "critical": "#ef4444",  # Red
    }

    def __init__(self):
        self.history: List[Dict] = []

    def calculate_score(
        self, analysis_results: Dict[str, Dict], checklist_results: Dict = None
    ) -> Dict:
        """
        Calculate comprehensive sensitivity score.

        Args:
            analysis_results: Dict from ContentAnalyzer.analyze()
            checklist_results: Optional results from WomenSafetyChecker

        Returns:
            Comprehensive scoring report
        """
        category_scores = {}
        weighted_sum = 0
        total_weight = 0

        for category, weight in self.WEIGHTS.items():
            if category in analysis_results:
                score_data = analysis_results[category]
                # Handle both dict and object
                if hasattr(score_data, "score"):
                    score = score_data.score
                    risk_level = (
                        score_data.risk_level.value
                        if hasattr(score_data.risk_level, "value")
                        else score_data.risk_level
                    )
                else:
                    score = score_data.get("score", 0)
                    risk_level = score_data.get("risk_level", "safe")

                category_scores[category] = RiskScore(
                    category=category,
                    score=score * 100,
                    risk_level=risk_level,
                    color=self.COLORS.get(risk_level, "#6b7280"),
                )

                weighted_sum += score * weight
                total_weight += weight
            else:
                category_scores[category] = RiskScore(
                    category=category,
                    score=0,
                    risk_level="safe",
                    color=self.COLORS["safe"],
                )

        # Normalize overall score
        overall_score = (weighted_sum / total_weight * 100) if total_weight > 0 else 0

        # Determine overall risk level
        if overall_score < 20:
            overall_risk = "safe"
        elif overall_score < 40:
            overall_risk = "low"
        elif overall_score < 60:
            overall_risk = "medium"
        elif overall_score < 80:
            overall_risk = "high"
        else:
            overall_risk = "critical"

        # Add checklist score if available
        checklist_score = 0
        if checklist_results:
            checklist_score = checklist_results.get("score", 0)
            # Weight checklist at 30% alongside analysis
            overall_score = overall_score * 0.7 + checklist_score * 0.3

        # Determine verdict
        verdict = self._get_verdict(overall_score, category_scores, checklist_results)

        # Generate warnings
        warnings = self._generate_warnings(category_scores, checklist_results)

        return {
            "overall_score": round(overall_score, 1),
            "overall_risk": overall_risk,
            "overall_color": self.COLORS.get(overall_risk, "#6b7280"),
            "verdict": verdict,
            "category_scores": {
                cat: score.to_dict() for cat, score in category_scores.items()
            },
            "checklist_score": checklist_score,
            "warnings": warnings,
            "can_post": overall_risk in ["safe", "low"],
            "needs_review": overall_risk == "medium",
            "do_not_post": overall_risk in ["high", "critical"],
        }

    def _get_verdict(
        self,
        score: float,
        category_scores: Dict[str, RiskScore],
        checklist_results: Dict = None,
    ) -> str:
        """Determine final verdict."""

        # Check for critical categories
        critical_categories = ["women_safety", "privacy", "harassment"]
        has_critical = any(
            category_scores.get(cat, RiskScore(cat, 0, "safe", "#22c55e")).risk_level
            in ["high", "critical"]
            for cat in critical_categories
        )

        if score >= 80 and not has_critical:
            return "SAFE TO POST"
        elif score >= 60 and not has_critical:
            return "REVIEW RECOMMENDED"
        elif score >= 40:
            return "REVISIONS NEEDED"
        else:
            return "DO NOT POST"

    def _generate_warnings(
        self, category_scores: Dict[str, RiskScore], checklist_results: Dict = None
    ) -> List[str]:
        """Generate specific warnings based on scores."""
        warnings = []

        # Category-specific warnings
        category_warnings = {
            "women_safety": "Women's safety concerns detected",
            "privacy": "Privacy violations possible",
            "violence": "Violent content present",
            "sexual_content": "Sexual content detected",
            "harassment": "Harassment indicators found",
            "legal": "Potential legal issues",
            "cultural_sensitivity": "Cultural sensitivity concerns",
            "self_harm": "Self-harm content detected",
            "dangerous_activities": "Dangerous activities shown",
            "misinformation": "Misinformation risk",
        }

        for cat, score in category_scores.items():
            if score.risk_level in ["high", "critical"]:
                warnings.append(category_warnings.get(cat, f"{cat} issue"))

        # Checklist warnings
        if checklist_results:
            if checklist_results.get("critical_issues"):
                warnings.append(
                    f"{len(checklist_results['critical_issues'])} critical consent/safety issues"
                )

        return warnings

    def generate_badge(self, score_data: Dict) -> str:
        """Generate HTML/CSS badge for embedding."""
        verdict = score_data.get("verdict", "UNKNOWN")
        color = score_data.get("overall_color", "#6b7280")
        score = score_data.get("overall_score", 0)

        return f"""
        <div style="
            display: inline-flex;
            align-items: center;
            gap: 8px;
            padding: 8px 16px;
            background: {color}20;
            border: 2px solid {color};
            border-radius: 20px;
            font-family: system-ui, sans-serif;
        ">
            <span style="font-size: 20px;">
                {"✓" if verdict == "SAFE TO POST" else "⚠" if "REVIEW" in verdict else "✗"}
            </span>
            <span style="color: {color}; font-weight: bold;">{verdict}</span>
            <span style="color: #6b7280; font-size: 12px;">({score}%)</span>
        </div>
        """


class QuickScorer:
    """
    Simple, fast scoring for quick checks.
    """

    @staticmethod
    def score_video(video_info: Dict) -> Dict:
        """
        Quick score based on basic video info.

        Args:
            video_info: Dict with title, description, tags

        Returns:
            Quick assessment
        """
        title = video_info.get("title", "").lower()
        description = video_info.get("description", "").lower()
        tags = " ".join(video_info.get("tags", [])).lower()

        content = f"{title} {description} {tags}"

        risk_indicators = 0
        concerns = []

        # Check high-risk keywords
        high_risk = [
            "prank",
            "challenge",
            "roast",
            "expose",
            "leak",
            "girls",
            "college",
            "hot",
            "sexy",
            "reaction",
        ]

        for keyword in high_risk:
            if keyword in content:
                risk_indicators += 1
                concerns.append(f"Contains '{keyword}'")

        # Calculate quick score
        if risk_indicators >= 4:
            quick_verdict = "REVIEW"
            quick_score = 60
            color = "#eab308"
        elif risk_indicators >= 2:
            quick_verdict = "CAUTION"
            quick_score = 75
            color = "#22c55e"
        else:
            quick_verdict = "LIKELY SAFE"
            quick_score = 90
            color = "#22c55e"

        return {
            "quick_score": quick_score,
            "verdict": quick_verdict,
            "color": color,
            "risk_indicators": risk_indicators,
            "concerns": concerns,
            "recommendation": QuickScorer._get_recommendation(quick_verdict),
        }

    @staticmethod
    def _get_recommendation(verdict: str) -> str:
        recommendations = {
            "LIKELY SAFE": "Content appears safe. Run full analysis for detailed check.",
            "CAUTION": "Some risk indicators found. Review content before posting.",
            "REVIEW": "Multiple risk indicators. Run full analysis before posting.",
        }
        return recommendations.get(verdict, "")
