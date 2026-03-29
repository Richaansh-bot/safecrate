"""
Content Safety Analysis Engine
Analyzes video content for safety concerns across multiple categories.
"""

from dataclasses import dataclass, field
from typing import Dict, List, Optional
from enum import Enum
import json


class RiskLevel(Enum):
    SAFE = "safe"
    LOW = "low"
    MEDIUM = "medium"
    HIGH = "high"
    CRITICAL = "critical"

    def color(self) -> str:
        colors = {
            "safe": "#22c55e",  # Green
            "low": "#84cc16",  # Lime
            "medium": "#eab308",  # Yellow
            "high": "#f97316",  # Orange
            "critical": "#ef4444",  # Red
        }
        return colors.get(self.value, "#6b7280")

    def emoji(self) -> str:
        emojis = {
            "safe": "✓",
            "low": "⚠",
            "medium": "⚡",
            "high": "🚨",
            "critical": "⛔",
        }
        return emojis.get(self.value, "?")


class ContentCategory(Enum):
    VIOLENCE = "violence"
    SEXUAL_CONTENT = "sexual_content"
    HARASSMENT = "harassment"
    PRIVACY = "privacy"
    MISINFORMATION = "misinformation"
    WOMEN_SAFETY = "women_safety"
    CULTURAL_SENSITIVITY = "cultural_sensitivity"
    LEGAL = "legal"
    SELF_HARM = "self_harm"
    DANGEROUS_ACTIVITIES = "dangerous_activities"


@dataclass
class Evidence:
    """Represents a single piece of evidence that contributed to the analysis."""

    keyword: str
    location: str  # "title", "description", "tags", "transcript"
    context: str  # The text snippet containing the keyword
    weight: float  # How much this contributed to the score
    severity: str = "medium"  # "low", "medium", "high", "critical"

    def to_dict(self) -> dict:
        return {
            "keyword": self.keyword,
            "location": self.location,
            "context": self.context[:200] + "..."
            if len(self.context) > 200
            else self.context,
            "weight": round(self.weight * 100, 1),
            "severity": self.severity,
        }


@dataclass
class AnalysisResult:
    category: ContentCategory
    score: float  # 0.0 to 1.0
    risk_level: RiskLevel
    findings: List[str] = field(default_factory=list)
    evidence: List[Evidence] = field(default_factory=list)
    recommendations: List[str] = field(default_factory=list)
    timestamp: str = ""

    def __post_init__(self):
        if self.score < 0.2:
            self.risk_level = RiskLevel.SAFE
        elif self.score < 0.4:
            self.risk_level = RiskLevel.LOW
        elif self.score < 0.6:
            self.risk_level = RiskLevel.MEDIUM
        elif self.score < 0.8:
            self.risk_level = RiskLevel.HIGH
        else:
            self.risk_level = RiskLevel.CRITICAL

    def to_dict(self) -> dict:
        return {
            "category": self.category.value,
            "score": self.score,
            "risk_level": self.risk_level.value,
            "findings": self.findings,
            "evidence": [e.to_dict() for e in self.evidence],
            "recommendations": self.recommendations,
            "total_evidence_count": len(self.evidence),
        }


@dataclass
class VideoMetadata:
    title: str = ""
    description: str = ""
    tags: List[str] = field(default_factory=list)
    thumbnail_url: str = ""
    duration_seconds: int = 0
    has_audio: bool = True
    has_video: bool = True
    language: str = "en"
    region_focus: str = "india"


class ContentAnalyzer:
    """
    Main content analysis engine.
    Analyzes video metadata, descriptions, and simulated frame analysis.
    """

    def __init__(self):
        self.categories = {
            ContentCategory.VIOLENCE: ViolenceAnalyzer(),
            ContentCategory.SEXUAL_CONTENT: SexualContentAnalyzer(),
            ContentCategory.HARASSMENT: HarassmentAnalyzer(),
            ContentCategory.PRIVACY: PrivacyAnalyzer(),
            ContentCategory.MISINFORMATION: MisinformationAnalyzer(),
            ContentCategory.WOMEN_SAFETY: WomenSafetyAnalyzer(),
            ContentCategory.CULTURAL_SENSITIVITY: CulturalAnalyzer(),
            ContentCategory.LEGAL: LegalAnalyzer(),
            ContentCategory.SELF_HARM: SelfHarmAnalyzer(),
            ContentCategory.DANGEROUS_ACTIVITIES: DangerousActivitiesAnalyzer(),
        }

        # Sensitivity weights for Indian context
        self.weights = {
            ContentCategory.VIOLENCE: 0.15,
            ContentCategory.SEXUAL_CONTENT: 0.18,
            ContentCategory.HARASSMENT: 0.15,
            ContentCategory.PRIVACY: 0.12,
            ContentCategory.MISINFORMATION: 0.08,
            ContentCategory.WOMEN_SAFETY: 0.20,  # Highest weight
            ContentCategory.CULTURAL_SENSITIVITY: 0.10,
            ContentCategory.LEGAL: 0.12,
            ContentCategory.SELF_HARM: 0.08,
            ContentCategory.DANGEROUS_ACTIVITIES: 0.10,
        }

    def analyze(
        self,
        video_path: Optional[str] = None,
        metadata: Optional[VideoMetadata] = None,
        analysis_data: Optional[Dict] = None,
    ) -> Dict[str, AnalysisResult]:
        """
        Analyze content and return results for all categories.
        """
        results = {}

        for category, analyzer in self.categories.items():
            if category == ContentCategory.WOMEN_SAFETY:
                # Women safety needs full context
                result = analyzer.analyze(metadata, analysis_data)
            else:
                result = analyzer.analyze(metadata, analysis_data)

            results[category.value] = result

        return results

    def calculate_overall_risk(
        self, results: Dict[str, AnalysisResult]
    ) -> tuple[float, RiskLevel]:
        """Calculate weighted overall risk score."""
        weighted_sum = 0
        for category, result in results.items():
            weight = self.weights.get(ContentCategory(category), 0.1)
            weighted_sum += result.score * weight

        score = min(1.0, weighted_sum)

        if score < 0.2:
            level = RiskLevel.SAFE
        elif score < 0.4:
            level = RiskLevel.LOW
        elif score < 0.6:
            level = RiskLevel.MEDIUM
        elif score < 0.8:
            level = RiskLevel.HIGH
        else:
            level = RiskLevel.CRITICAL

        return score, level


class BaseAnalyzer:
    """Base class for category analyzers."""

    # Keywords and patterns for detection (would be ML model in production)
    VIOLENCE_KEYWORDS = [
        "fight",
        "attack",
        "blood",
        "weapon",
        "gun",
        "knife",
        "murder",
        "assault",
        "riot",
        "violence",
        "beating",
        "punch",
        "slap",
        "abuse",
        "torture",
        # Hindi/Indian context
        "marpit",
        "hano",
        "lathi",
        "aatank",
        "goli",
    ]

    SEXUAL_KEYWORDS = [
        "nude",
        "naked",
        "sex",
        "porn",
        "xxx",
        "bikini",
        "lingerie",
        "provocative",
        "explicit",
        "nsfw",
        "hot",
        "bedroom",
        # Hindi/Indian context (slang)
        "nanga",
        "chotha",
        "gaand",
        "lund",
        "chut",
        "bhosda",
        "gaand mara",
        "lund mara",
    ]

    HARASSMENT_KEYWORDS = [
        "slut",
        "whore",
        "bitch",
        "rape",
        "molest",
        "harass",
        "stalk",
        "abuse",
        "bullies",
        "humiliate",
        "mock",
        "tease",
        "chamak",
        "dhat",
        "behenchod",
        "bhenchod",
        "madarchod",
        "bhadwa",
        "kutta",
        "saala",
        "chutiya",
        "bsdk",
        "harami",
        "randi",
        "nautanki",
        "haggu",
    ]

    WOMEN_SAFETY_KEYWORDS = [
        "girl",
        "women",
        "female",
        "lady",
        "beti",
        "aurat",
        "mahal",
        "beti",
        "daughter",
        "sister",
        "mother",
        "wife",
        "uncle",
        "aunty",
        "didi",
        "unsafe",
        "danger",
        "attack",
        "assault",
        "harassment",
        "eve tease",
        "stalking",
        "voyeur",
        "hidden camera",
        "bathroom",
        "changing room",
    ]

    def analyze(
        self, metadata: Optional[VideoMetadata], data: Optional[Dict]
    ) -> AnalysisResult:
        raise NotImplementedError


class ViolenceAnalyzer(BaseAnalyzer):
    def _get_context(self, text: str, keyword: str, window: int = 50) -> str:
        """Extract context around a keyword."""
        text_lower = text.lower()
        idx = text_lower.find(keyword.lower())
        if idx == -1:
            return keyword
        start = max(0, idx - window)
        end = min(len(text), idx + len(keyword) + window)
        context = text[start:end].strip()
        return "..." + context + "..." if start > 0 or end < len(text) else context

    def analyze(
        self, metadata: Optional[VideoMetadata], data: Optional[Dict]
    ) -> AnalysisResult:
        score = 0.0
        findings = []
        evidence = []

        # Prepare text sources
        sources = {}
        if metadata:
            if metadata.title:
                sources["title"] = metadata.title
            if metadata.description:
                sources["description"] = metadata.description
            if metadata.tags:
                sources["tags"] = ", ".join(metadata.tags)
        if data and "transcript" in data:
            sources["transcript"] = data["transcript"]

        # Check for violence indicators in each source
        for location, text in sources.items():
            text_lower = text.lower()
            for keyword in self.VIOLENCE_KEYWORDS:
                if keyword in text_lower:
                    context = self._get_context(text, keyword)
                    ev = Evidence(
                        keyword=keyword,
                        location=location,
                        context=context,
                        weight=0.15,
                        severity="medium"
                        if keyword in ["fight", "punch", "slap"]
                        else "high",
                    )
                    evidence.append(ev)
                    findings.append(f"Found '{keyword}' in {location}")

        violence_count = len(evidence)
        if violence_count >= 3:
            score = min(1.0, 0.4 + (violence_count - 3) * 0.1)
        elif violence_count > 0:
            score = min(0.6, violence_count * 0.15)

        # Check for graphic content indicators
        graphic_evidence = []
        graphic_indicators = ["blood", "gore", "graphic", "warning", "disturbing"]
        for location, text in sources.items():
            text_lower = text.lower()
            for keyword in graphic_indicators:
                if keyword in text_lower:
                    context = self._get_context(text, keyword)
                    ev = Evidence(
                        keyword=keyword,
                        location=location,
                        context=context,
                        weight=0.2,
                        severity="high",
                    )
                    graphic_evidence.append(ev)
                    findings.append(f"Graphic indicator '{keyword}' in {location}")
        if graphic_evidence:
            score = max(score, 0.6)
            evidence.extend(graphic_evidence)

        # Recommendations
        recommendations = []
        if score > 0.3:
            recommendations.append("Consider adding content warning at video start")
            recommendations.append("Remove or blur graphic elements")
            recommendations.append("Ensure violence is not glorified")

        return AnalysisResult(
            category=ContentCategory.VIOLENCE,
            score=score,
            risk_level=RiskLevel.SAFE,
            findings=findings,
            evidence=evidence,
            recommendations=recommendations,
        )


class SexualContentAnalyzer(BaseAnalyzer):
    def _get_context(self, text: str, keyword: str, window: int = 50) -> str:
        text_lower = text.lower()
        idx = text_lower.find(keyword.lower())
        if idx == -1:
            return keyword
        start = max(0, idx - window)
        end = min(len(text), idx + len(keyword) + window)
        context = text[start:end].strip()
        return "..." + context + "..." if start > 0 or end < len(text) else context

    def analyze(
        self, metadata: Optional[VideoMetadata], data: Optional[Dict]
    ) -> AnalysisResult:
        score = 0.0
        findings = []
        evidence = []

        # Prepare text sources
        sources = {}
        if metadata:
            if metadata.title:
                sources["title"] = metadata.title
            if metadata.description:
                sources["description"] = metadata.description
            if metadata.tags:
                sources["tags"] = ", ".join(metadata.tags)
        if data and "transcript" in data:
            sources["transcript"] = data["transcript"]

        # Check for sexual content indicators
        for location, text in sources.items():
            text_lower = text.lower()
            for keyword in self.SEXUAL_KEYWORDS:
                if keyword in text_lower:
                    context = self._get_context(text, keyword)
                    severity = (
                        "high"
                        if keyword in ["porn", "nude", "naked", "sex"]
                        else "medium"
                    )
                    ev = Evidence(
                        keyword=keyword,
                        location=location,
                        context=context,
                        weight=0.2,
                        severity=severity,
                    )
                    evidence.append(ev)
                    findings.append(f"Found '{keyword}' in {location}")

        sexual_count = len(evidence)
        if sexual_count >= 1:
            score = min(1.0, 0.5 + sexual_count * 0.15)

        # Age-restricted indicators
        age_restricted = [
            "18+",
            "adult",
            "mature",
            "parental guidance",
            "explicit content",
        ]
        for location, text in sources.items():
            text_lower = text.lower()
            for keyword in age_restricted:
                if keyword.lower() in text_lower:
                    context = self._get_context(text, keyword)
                    ev = Evidence(
                        keyword=keyword,
                        location=location,
                        context=context,
                        weight=0.15,
                        severity="medium",
                    )
                    evidence.append(ev)
                    findings.append(f"Age-restricted marker '{keyword}' in {location}")
        if any(
            kw.lower() in " ".join(sources.values()).lower() for kw in age_restricted
        ):
            score = max(score, 0.4)

        recommendations = []
        if score > 0.3:
            recommendations.append("Mark video as age-restricted")
            recommendations.append("Ensure no non-consensual content")
            recommendations.append("Review platform-specific guidelines")

        return AnalysisResult(
            category=ContentCategory.SEXUAL_CONTENT,
            score=score,
            risk_level=RiskLevel.SAFE,
            findings=findings,
            evidence=evidence,
            recommendations=recommendations,
        )


class HarassmentAnalyzer(BaseAnalyzer):
    def _get_context(self, text: str, keyword: str, window: int = 50) -> str:
        text_lower = text.lower()
        idx = text_lower.find(keyword.lower())
        if idx == -1:
            return keyword
        start = max(0, idx - window)
        end = min(len(text), idx + len(keyword) + window)
        context = text[start:end].strip()
        return "..." + context + "..." if start > 0 or end < len(text) else context

    def analyze(
        self, metadata: Optional[VideoMetadata], data: Optional[Dict]
    ) -> AnalysisResult:
        score = 0.0
        findings = []
        evidence = []

        # Prepare text sources
        sources = {}
        if metadata:
            if metadata.title:
                sources["title"] = metadata.title
            if metadata.description:
                sources["description"] = metadata.description
            if metadata.tags:
                sources["tags"] = ", ".join(metadata.tags)
        if data and "transcript" in data:
            sources["transcript"] = data["transcript"]

        # Check for harassment indicators
        for location, text in sources.items():
            text_lower = text.lower()
            for keyword in self.HARASSMENT_KEYWORDS:
                if keyword in text_lower:
                    context = self._get_context(text, keyword)
                    severity = (
                        "high"
                        if keyword in ["rape", "molest", "slut", "whore"]
                        else "medium"
                    )
                    ev = Evidence(
                        keyword=keyword,
                        location=location,
                        context=context,
                        weight=0.2,
                        severity=severity,
                    )
                    evidence.append(ev)
                    findings.append(f"Found '{keyword}' in {location}")

        harassment_count = len(evidence)
        if harassment_count >= 1:
            score = min(1.0, 0.6 + harassment_count * 0.1)

        # Targeting indicators
        targeting = ["against", "target", "expose", "call out", "shame"]
        for location, text in sources.items():
            text_lower = text.lower()
            for keyword in targeting:
                if keyword in text_lower:
                    context = self._get_context(text, keyword)
                    ev = Evidence(
                        keyword=keyword,
                        location=location,
                        context=context,
                        weight=0.15,
                        severity="medium",
                    )
                    evidence.append(ev)
                    findings.append(f"Targeting term '{keyword}' in {location}")

        # Check for targeting evidence
        targeting_evidence = [e for e in evidence if e.keyword in targeting]
        if targeting_evidence:
            score = max(score, 0.5)

        # Comedy-specific risks - standup often uses slurs
        comedy_risks = [
            "standup",
            "comedian",
            "open mic",
            "crowd work",
            "roast",
            "bantai",
        ]
        comedy_evidence = []
        for location, text in sources.items():
            text_lower = text.lower()
            for keyword in comedy_risks:
                if keyword in text_lower:
                    context = self._get_context(text, keyword)
                    ev = Evidence(
                        keyword=keyword,
                        location=location,
                        context=context,
                        weight=0.1,
                        severity="low",
                    )
                    comedy_evidence.append(ev)
        if comedy_evidence and harassment_count > 0:
            evidence.extend(comedy_evidence)
            score = max(score, 0.7)
            findings.append(
                "Comedy content with potential slurs - review for offensive language"
            )

        recommendations = []
        if score > 0.3:
            recommendations.append("Ensure targeted individuals consented")
            recommendations.append("Review defamation laws before posting")
            recommendations.append("Consider constructive criticism approach")

        return AnalysisResult(
            category=ContentCategory.HARASSMENT,
            score=score,
            risk_level=RiskLevel.SAFE,
            findings=findings,
            evidence=evidence,
            recommendations=recommendations,
        )


class PrivacyAnalyzer(BaseAnalyzer):
    def _get_context(self, text: str, keyword: str, window: int = 50) -> str:
        text_lower = text.lower()
        idx = text_lower.find(keyword.lower())
        if idx == -1:
            return keyword
        start = max(0, idx - window)
        end = min(len(text), idx + len(keyword) + window)
        context = text[start:end].strip()
        return "..." + context + "..." if start > 0 or end < len(text) else context

    def analyze(
        self, metadata: Optional[VideoMetadata], data: Optional[Dict]
    ) -> AnalysisResult:
        score = 0.0
        findings = []
        evidence = []

        # Prepare text sources
        sources = {}
        if metadata:
            if metadata.title:
                sources["title"] = metadata.title
            if metadata.description:
                sources["description"] = metadata.description
            if metadata.tags:
                sources["tags"] = ", ".join(metadata.tags)

        privacy_keywords = [
            "leak",
            "expose",
            "private",
            "personal",
            "address",
            "phone",
            "number",
            "aadhaar",
            "pan card",
            "bank",
            "secret",
            "hidden",
            "bathroom",
            "changing room",
            "voyeur",
            "spy cam",
            "hidden camera",
        ]

        for location, text in sources.items():
            text_lower = text.lower()
            for keyword in privacy_keywords:
                if keyword in text_lower:
                    context = self._get_context(text, keyword)
                    severity = (
                        "high"
                        if keyword in ["voyeur", "hidden camera", "spy cam", "bathroom"]
                        else "medium"
                    )
                    ev = Evidence(
                        keyword=keyword,
                        location=location,
                        context=context,
                        weight=0.25,
                        severity=severity,
                    )
                    evidence.append(ev)
                    findings.append(f"Found '{keyword}' in {location}")

        privacy_count = len(evidence)
        if privacy_count >= 1:
            score = min(1.0, 0.6 + privacy_count * 0.1)

        # Hidden camera indicators - critical
        hidden_critical = ["voyeur", "hidden camera", "spy cam"]
        for location, text in sources.items():
            text_lower = text.lower()
            for keyword in hidden_critical:
                if keyword in text_lower:
                    context = self._get_context(text, keyword)
                    ev = Evidence(
                        keyword=keyword,
                        location=location,
                        context=context,
                        weight=0.35,
                        severity="critical",
                    )
                    evidence.append(ev)
                    findings.append(f"CRITICAL: {keyword} detected in {location}")

        if any(e.keyword in hidden_critical for e in evidence):
            score = max(score, 0.8)

        recommendations = []
        if score > 0.3:
            recommendations.append("Remove any personally identifiable information")
            recommendations.append("Ensure consent from all individuals shown")
            recommendations.append("Blur faces of non-consenting individuals")

        return AnalysisResult(
            category=ContentCategory.PRIVACY,
            score=score,
            risk_level=RiskLevel.SAFE,
            findings=findings,
            evidence=evidence,
            recommendations=recommendations,
        )


class MisinformationAnalyzer(BaseAnalyzer):
    def analyze(
        self, metadata: Optional[VideoMetadata], data: Optional[Dict]
    ) -> AnalysisResult:
        score = 0.0
        findings = []

        text_content = ""
        if metadata:
            text_content = (
                f"{metadata.title} {metadata.description} {' '.join(metadata.tags)}"
            )

        text_lower = text_content.lower()

        misinformation_indicators = [
            "fake",
            "hoax",
            "conspiracy",
            "they don't want you",
            "truth exposed",
            "mainstream media won't show",
        ]

        misinfo_count = sum(1 for ind in misinformation_indicators if ind in text_lower)
        if misinfo_count >= 2:
            score = min(1.0, 0.4 + misinfo_count * 0.1)
            findings.append("Potential misinformation patterns detected")

        recommendations = []
        if score > 0.3:
            recommendations.append("Provide sources for all claims")
            recommendations.append("Clearly label opinion vs fact")
            recommendations.append("Avoid sensationalist language")

        return AnalysisResult(
            category=ContentCategory.MISINFORMATION,
            score=score,
            risk_level=RiskLevel.SAFE,
            findings=findings,
            recommendations=recommendations,
        )


class WomenSafetyAnalyzer(BaseAnalyzer):
    """
    Special analyzer for women's safety in Indian context.
    This is the most critical category for the platform.
    """

    def _get_context(self, text: str, keyword: str, window: int = 50) -> str:
        text_lower = text.lower()
        idx = text_lower.find(keyword.lower())
        if idx == -1:
            return keyword
        start = max(0, idx - window)
        end = min(len(text), idx + len(keyword) + window)
        context = text[start:end].strip()
        return "..." + context + "..." if start > 0 or end < len(text) else context

    # Specific patterns for women's safety concerns in India
    UNSAFE_PORTRAYAL = [
        "victim",
        "prey",
        "damsel",
        "damsel in distress",
        "eve teasing",
        "molestation",
        "acid attack",
    ]

    GLORIFICATION = [
        "roast",
        "prank gone wrong",
        "challenge",
        "dare",
        "social experiment",
        "hidden camera prank",
    ]

    EXPLOITATION = [
        "reaction video",
        "reacting to",
        "watching",
        "girls reacting",
        "mumbai",
        "delhi",
        "bangalore",
        "college girls",
    ]

    BODY_SHAMING = [
        "fat",
        "ugly",
        "skinny",
        "dark",
        "fair",
        "beautiful",
        "sexy",
        "hot",
        "looks",
        "appearance",
    ]

    VOYEUR_KEYWORDS = [
        "bathroom",
        "changing room",
        "college",
        "hostel",
        "bedroom",
        "sleeping",
        "without consent",
        "secret",
        "prank",
    ]

    def analyze(
        self, metadata: Optional[VideoMetadata], data: Optional[Dict]
    ) -> AnalysisResult:
        score = 0.0
        findings = []
        evidence = []

        # Prepare text sources
        sources = {}
        if metadata:
            if metadata.title:
                sources["title"] = metadata.title
            if metadata.description:
                sources["description"] = metadata.description
            if metadata.tags:
                sources["tags"] = ", ".join(metadata.tags)
        if data and "transcript" in data:
            sources["transcript"] = data["transcript"]

        # Check for unsafe portrayal
        for location, text in sources.items():
            text_lower = text.lower()
            for keyword in self.UNSAFE_PORTRAYAL:
                if keyword in text_lower:
                    context = self._get_context(text, keyword)
                    ev = Evidence(
                        keyword=keyword,
                        location=location,
                        context=context,
                        weight=0.25,
                        severity="high",
                    )
                    evidence.append(ev)
                    findings.append(f"Unsafe portrayal: '{keyword}' in {location}")

        # Check for glorification patterns
        for location, text in sources.items():
            text_lower = text.lower()
            for keyword in self.GLORIFICATION:
                if keyword in text_lower:
                    context = self._get_context(text, keyword)
                    ev = Evidence(
                        keyword=keyword,
                        location=location,
                        context=context,
                        weight=0.15,
                        severity="medium",
                    )
                    evidence.append(ev)
                    findings.append(f"Challenge/prank: '{keyword}' in {location}")

        # Check for exploitation patterns
        for location, text in sources.items():
            text_lower = text.lower()
            for keyword in self.EXPLOITATION:
                if keyword in text_lower:
                    context = self._get_context(text, keyword)
                    ev = Evidence(
                        keyword=keyword,
                        location=location,
                        context=context,
                        weight=0.15,
                        severity="medium",
                    )
                    evidence.append(ev)
                    findings.append(f"Exploitation risk: '{keyword}' in {location}")

        # Check for voyeurism (CRITICAL)
        voyeur_evidence = []
        for location, text in sources.items():
            text_lower = text.lower()
            for keyword in self.VOYEUR_KEYWORDS:
                if keyword in text_lower:
                    context = self._get_context(text, keyword)
                    severity = (
                        "critical"
                        if keyword in ["bathroom", "changing room"]
                        else "high"
                    )
                    ev = Evidence(
                        keyword=keyword,
                        location=location,
                        context=context,
                        weight=0.3,
                        severity=severity,
                    )
                    voyeur_evidence.append(ev)
                    findings.append(f"CRITICAL: '{keyword}' in {location}")

        if len(voyeur_evidence) >= 2:
            score = max(score, 0.9)
            evidence.extend(voyeur_evidence)

        # Calculate risk score
        if len([e for e in evidence if e.keyword in self.UNSAFE_PORTRAYAL]) > 0:
            score = max(score, 0.7)
        if len([e for e in evidence if e.keyword in self.EXPLOITATION]) >= 2:
            score = max(score, 0.65)
        if len([e for e in evidence if e.keyword in self.GLORIFICATION]) >= 2:
            score = max(score, 0.55)

        # Recommendations
        recommendations = []
        if score > 0.4:
            recommendations.append(
                "CRITICAL: Ensure all women shown have given explicit consent"
            )
            recommendations.append("Review portrayal of women - avoid stereotypes")
            recommendations.append("Remove any content filmed without consent")
            recommendations.append(
                "Add trigger warnings if discussing sensitive topics"
            )

        if score > 0.6:
            recommendations.append(
                "STRONGLY RECOMMEND: Have a woman review this content"
            )
            recommendations.append("Consider the impact on women's safety community")
            recommendations.append("This content may make women feel unsafe")

        risk_level = RiskLevel.SAFE
        if score >= 0.9:
            risk_level = RiskLevel.CRITICAL
        elif score >= 0.7:
            risk_level = RiskLevel.HIGH
        elif score >= 0.5:
            risk_level = RiskLevel.MEDIUM
        elif score >= 0.3:
            risk_level = RiskLevel.LOW

        return AnalysisResult(
            category=ContentCategory.WOMEN_SAFETY,
            score=score,
            risk_level=risk_level,
            findings=findings,
            evidence=evidence,
            recommendations=recommendations,
        )


class CulturalAnalyzer(BaseAnalyzer):
    def analyze(
        self, metadata: Optional[VideoMetadata], data: Optional[Dict]
    ) -> AnalysisResult:
        score = 0.0
        findings = []

        text_content = ""
        if metadata:
            text_content = (
                f"{metadata.title} {metadata.description} {' '.join(metadata.tags)}"
            )

        text_lower = text_content.lower()

        # Religious sensitivity (India context)
        religions = [
            "hindu",
            "muslim",
            "christian",
            "sikh",
            "buddhist",
            "jain",
            "parsi",
        ]
        religious_mentions = sum(1 for r in religions if r in text_lower)

        # Controversial religious terms
        religious_controversy = [
            "temple",
            "mosque",
            "church",
            "gurudwara",
            "madrasa",
            "cow",
            "halal",
            "bakra",
            "pakistani",
            "-terrorism",
        ]
        controversy_count = sum(1 for kw in religious_controversy if kw in text_lower)

        if controversy_count >= 3:
            score = max(score, 0.5)
            findings.append(
                "Multiple religious/cultural terms detected - exercise caution"
            )

        # Caste sensitivity
        caste_terms = [
            " caste",
            "upper caste",
            "lower caste",
            "obc",
            "sc/st",
            "brahmin",
            "thakur",
            "jaat",
            "baniya",
        ]
        caste_count = sum(1 for kw in caste_terms if kw in text_lower)
        if caste_count >= 1:
            score = max(score, 0.6)
            findings.append("Caste-related content detected - HIGH SENSITIVITY")

        # Regional offense
        regional = [
            "bengali",
            "south indian",
            "north indian",
            "bihari",
            "up",
            "bihar",
            "mumbai",
            "delhi",
        ]
        regional_count = sum(1 for kw in regional if kw in text_lower)
        if regional_count >= 2:
            score = max(score, 0.3)
            findings.append("Regional stereotypes may be present")

        recommendations = []
        if score > 0.3:
            recommendations.append("Ensure respectful portrayal of all religions")
            recommendations.append("Avoid stereotypes and generalizations")
            recommendations.append("Consider diverse audience perspectives")

        return AnalysisResult(
            category=ContentCategory.CULTURAL_SENSITIVITY,
            score=score,
            risk_level=RiskLevel.SAFE,
            findings=findings,
            recommendations=recommendations,
        )


class LegalAnalyzer(BaseAnalyzer):
    """Indian legal compliance checker."""

    def analyze(
        self, metadata: Optional[VideoMetadata], data: Optional[Dict]
    ) -> AnalysisResult:
        score = 0.0
        findings = []

        text_content = ""
        if metadata:
            text_content = (
                f"{metadata.title} {metadata.description} {' '.join(metadata.tags)}"
            )

        text_lower = text_content.lower()

        # IT Act violations
        it_act_keywords = [
            "obscene",
            "defamatory",
            "hate speech",
            "cybercrime",
            "impersonate",
            "fake account",
        ]
        it_violations = sum(1 for kw in it_act_keywords if kw in text_lower)

        if it_violations >= 2:
            score = max(score, 0.7)
            findings.append("Potential IT Act violation indicators")

        # IPC relevant keywords
        ipc_keywords = [
            "abet",
            "conspiracy",
            "murder",
            "theft",
            "robbery",
            "assault",
            "kidnap",
            "rape",
            "cheating",
            "fraud",
        ]
        ipc_violations = sum(1 for kw in ipc_keywords if kw in text_lower)
        if ipc_violations >= 1:
            score = max(score, 0.8)
            findings.append(
                f"IPC-relevant content ({ipc_violations} terms) - LEGAL REVIEW NEEDED"
            )

        # Copyright
        copyright_keywords = [
            "song",
            "music",
            "movie clip",
            "dialogue",
            "copyright",
            "licensed",
            "fair use",
        ]
        copyright_count = sum(1 for kw in copyright_keywords if kw in text_lower)
        if copyright_count >= 2:
            score = max(score, 0.4)
            findings.append("Copyrighted material may be used")

        recommendations = []
        if score > 0.4:
            recommendations.append("Review IT Act 2000 provisions")
            recommendations.append("Ensure no defamation or hate speech")
            recommendations.append("Obtain proper licenses for music/media")

        if ipc_violations > 0:
            recommendations.append("CONSULT LEGAL ADVISOR before posting")
            recommendations.append("Consider potential criminal liability")

        return AnalysisResult(
            category=ContentCategory.LEGAL,
            score=score,
            risk_level=RiskLevel.SAFE,
            findings=findings,
            recommendations=recommendations,
        )


class SelfHarmAnalyzer(BaseAnalyzer):
    def analyze(
        self, metadata: Optional[VideoMetadata], data: Optional[Dict]
    ) -> AnalysisResult:
        score = 0.0
        findings = []

        text_content = ""
        if metadata:
            text_content = (
                f"{metadata.title} {metadata.description} {' '.join(metadata.tags)}"
            )

        text_lower = text_content.lower()

        self_harm_keywords = [
            "suicide",
            "kill myself",
            "end my life",
            "depression",
            "self harm",
            "cutting",
            "overdose",
            "hang myself",
            "jump off",
            "don't want to live",
            "worthless",
        ]

        self_harm_count = sum(1 for kw in self_harm_keywords if kw in text_lower)
        if self_harm_count >= 1:
            score = min(1.0, 0.6 + self_harm_count * 0.1)
            findings.append("Self-harm related content detected")

        # Eating disorders
        eating_disorder_keywords = [
            "bulimia",
            "anorexia",
            "binge",
            "purge",
            "skip meal",
        ]
        if any(kw in text_lower for kw in eating_disorder_keywords):
            score = max(score, 0.5)
            findings.append("Eating disorder related content")

        recommendations = []
        if self_harm_count > 0:
            recommendations.append("Include helpline information (iCall: 9152987821)")
            recommendations.append("Add content warning at video start")
            recommendations.append("Consider whether this content is harmful")

        return AnalysisResult(
            category=ContentCategory.SELF_HARM,
            score=score,
            risk_level=RiskLevel.SAFE,
            findings=findings,
            recommendations=recommendations,
        )


class DangerousActivitiesAnalyzer(BaseAnalyzer):
    def analyze(
        self, metadata: Optional[VideoMetadata], data: Optional[Dict]
    ) -> AnalysisResult:
        score = 0.0
        findings = []

        text_content = ""
        if metadata:
            text_content = (
                f"{metadata.title} {metadata.description} {' '.join(metadata.tags)}"
            )

        text_lower = text_content.lower()

        dangerous_keywords = [
            "challenge",
            "stunt",
            "dangerous",
            "don't try at home",
            "roof top",
            "railway track",
            "high speed",
            "race",
            "car surfing",
            "skateboard",
            "trick",
            "flip",
        ]

        dangerous_count = sum(1 for kw in dangerous_keywords if kw in text_lower)
        if dangerous_count >= 2:
            score = min(1.0, 0.4 + dangerous_count * 0.1)
            findings.append(f"Dangerous activity indicators ({dangerous_count})")

        # India-specific dangerous locations
        india_dangerous = [
            "metro roof",
            "train roof",
            "bridge climbing",
            "tower climbing",
            "high voltage",
        ]
        if any(kw in text_lower for kw in india_dangerous):
            score = max(score, 0.8)
            findings.append("EXTREME DANGER: Life-threatening activity indicators")

        recommendations = []
        if dangerous_count >= 2:
            recommendations.append("Add prominent 'DO NOT TRY' warning")
            recommendations.append("Show safety measures taken")
            recommendations.append("Consider not promoting dangerous behavior")

        if score > 0.6:
            recommendations.append(
                "This content may influence young viewers dangerously"
            )

        return AnalysisResult(
            category=ContentCategory.DANGEROUS_ACTIVITIES,
            score=score,
            risk_level=RiskLevel.SAFE,
            findings=findings,
            recommendations=recommendations,
        )


# Type alias
from typing import Optional
