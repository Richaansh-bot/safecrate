"""
Indian Law Compliance Checker
Ensures content complies with Indian laws and regulations
"""

from dataclasses import dataclass
from typing import List, Dict


@dataclass
class LegalIssue:
    section: str
    act: str
    description: str
    severity: str  # "warning", "violation", "criminal"
    recommendation: str


class IndianLawChecker:
    """
    Checks content compliance with Indian laws relevant to digital content.

    Key laws covered:
    - IT Act 2000 and Amendments
    - IPC (Indian Penal Code)
    - POSH Act (Sexual Harassment)
    - CAA (Cinematograph Act)
    """

    def __init__(self):
        self.laws = self._build_law_database()

    def _build_law_database(self) -> Dict:
        return {
            "it_act_66a": {
                "act": "IT Act 2000",
                "section": "Section 66A",
                "description": "Sending offensive messages through communication services",
                "keywords": ["offensive", "menacing", "hoax"],
                "severity": "violation",
                "punishment": "Imprisonment up to 3 years, fine",
            },
            "it_act_66d": {
                "act": "IT Act 2000",
                "section": "Section 66D",
                "description": "Cheating by personation using computer resource",
                "keywords": ["impersonate", "fake", "stolen"],
                "severity": "violation",
                "punishment": "Imprisonment up to 3 years, fine",
            },
            "it_act_67": {
                "act": "IT Act 2000",
                "section": "Section 67",
                "description": "Publishing obscene information in electronic form",
                "keywords": ["obscene", "porn", "nude", "explicit"],
                "severity": "criminal",
                "punishment": "Imprisonment up to 5 years, fine up to 10 lakhs (first offense)",
            },
            "it_act_67a": {
                "act": "IT Act 2000 (Amended)",
                "section": "Section 67A",
                "description": "Publishing sexually explicit material",
                "keywords": ["sexually explicit", "adult content", "18+"],
                "severity": "criminal",
                "punishment": "Imprisonment up to 7 years, fine",
            },
            "ipc_292": {
                "act": "IPC",
                "section": "Section 292",
                "description": "Sale of obscene books etc.",
                "keywords": ["obscene", "indecent"],
                "severity": "violation",
                "punishment": "Fine, imprisonment up to 2 years (first offense)",
            },
            "ipc_354": {
                "act": "IPC",
                "section": "Section 354",
                "description": "Assault or criminal force to woman with intent to outrage her modesty",
                "keywords": ["molest", "eve tease", "harassment", "assault"],
                "severity": "criminal",
                "punishment": "Imprisonment up to 2 years, fine",
            },
            "ipc_354a": {
                "act": "IPC",
                "section": "Section 354A",
                "description": "Sexual harassment - unwelcome physical contact, advances",
                "keywords": ["unwanted", "harassment", "touch"],
                "severity": "criminal",
                "punishment": "Imprisonment up to 3 years, fine",
            },
            "ipc_354d": {
                "act": "IPC",
                "section": "Section 354D",
                "description": "Stalking - following, contacting to establish communication",
                "keywords": ["stalk", "following", "track"],
                "severity": "criminal",
                "punishment": "Imprisonment up to 3 years (first offense), 5 years (subsequent)",
            },
            "ipc_499": {
                "act": "IPC",
                "section": "Section 499",
                "description": "Defamation - harming someone's reputation",
                "keywords": ["defame", "libel", "slander", "expose"],
                "severity": "violation",
                "punishment": "Fine, imprisonment up to 2 years",
            },
            "ipc_503": {
                "act": "IPC",
                "section": "Section 503",
                "description": "Criminal intimidation",
                "keywords": ["threaten", "intimidate", "harm"],
                "severity": "violation",
                "punishment": "Imprisonment up to 2 years, fine",
            },
            "ipc_505": {
                "act": "IPC",
                "section": "Section 505",
                "description": "Statements creating or promoting enmity, hatred or ill-will",
                "keywords": ["hate speech", "enmity", "religious", "communal"],
                "severity": "criminal",
                "punishment": "Imprisonment up to 3 years, fine",
            },
            "posh_act": {
                "act": "POSH Act 2013",
                "section": "POSH",
                "description": "Sexual harassment at workplace",
                "keywords": ["workplace", "colleague", "boss"],
                "severity": "warning",
                "recommendation": "Ensure no workplace harassment depicted",
            },
            "privacy_right": {
                "act": "Digital Personal Data Protection Act 2023",
                "section": "DPDP",
                "description": "Processing personal data without consent",
                "keywords": ["personal data", "private", "consent", "leak"],
                "severity": "violation",
                "punishment": "Penalties up to Rs. 250 crore",
            },
        }

    def check_compliance(
        self,
        title: str = "",
        description: str = "",
        tags: List[str] = None,
        transcript: str = "",
    ) -> Dict:
        """
        Check content against Indian laws.

        Returns detailed compliance report.
        """
        if tags is None:
            tags = []

        content = f"{title} {description} {' '.join(tags)} {transcript}".lower()

        violations = []
        warnings = []

        for law_key, law_info in self.laws.items():
            # Check for keywords
            matches = [kw for kw in law_info.get("keywords", []) if kw in content]

            if matches:
                issue = LegalIssue(
                    section=law_info["section"],
                    act=law_info["act"],
                    description=law_info["description"],
                    severity=law_info["severity"],
                    recommendation=self._get_recommendation(law_info),
                )

                if law_info["severity"] == "criminal":
                    violations.append(issue)
                elif law_info["severity"] == "violation":
                    violations.append(issue)
                else:
                    warnings.append(issue)

        # Calculate compliance score
        if violations:
            criminal_count = sum(1 for v in violations if v.severity == "criminal")
            if criminal_count > 0:
                compliance_score = max(0, 30 - criminal_count * 15)
                verdict = "NON-COMPLIANT"
            else:
                compliance_score = max(0, 60 - len(violations) * 15)
                verdict = "PARTIAL COMPLIANCE"
        else:
            compliance_score = 100 - len(warnings) * 10
            verdict = "COMPLIANT" if compliance_score >= 80 else "NEEDS REVIEW"

        return {
            "compliance_score": compliance_score,
            "verdict": verdict,
            "violations": [
                {
                    "section": v.section,
                    "act": v.act,
                    "description": v.description,
                    "severity": v.severity,
                    "recommendation": v.recommendation,
                }
                for v in violations
            ],
            "warnings": [
                {
                    "section": w.section,
                    "act": w.act,
                    "description": w.description,
                    "recommendation": w.recommendation,
                }
                for w in warnings
            ],
            "can_post": compliance_score >= 70,
            "consult_lawyer": any(v.severity == "criminal" for v in violations),
        }

    def _get_recommendation(self, law_info: Dict) -> str:
        """Get specific recommendation based on law."""
        severity = law_info.get("severity", "warning")

        if severity == "criminal":
            return (
                f"CRITICAL: {law_info['description']}. "
                f"Potential {law_info['section']} under {law_info['act']}. "
                f"Consult a lawyer before posting. "
                f"Punishment: {law_info.get('punishment', 'See law')}"
            )
        elif severity == "violation":
            return (
                f"This content may violate {law_info['section']} of {law_info['act']}. "
                f"Review carefully or consult legal counsel. "
                f"Punishment: {law_info.get('punishment', 'See law')}"
            )
        else:
            return law_info.get("recommendation", "Exercise caution")

    def get_safe_harbor_tips(self) -> List[str]:
        """Tips for safe harbor under IT Act."""
        return [
            "Include content warnings for sensitive material",
            "Provide age verification or restrict access appropriately",
            "Remove content immediately if reported",
            "Maintain reporting mechanism for users",
            "Don't encourage or glorify illegal activities",
            "Respect privacy of individuals shown",
            "Avoid hate speech and communal content",
            "Don't post defamatory content without verification",
        ]

    def generate_disclaimer(self) -> str:
        """Generate legal disclaimer text."""
        return """
        LEGAL DISCLAIMER:
        This content safety check is for guidance only and does not constitute legal advice. 
        Compliance with the check does not guarantee legal safety. 
        For legal advice specific to your content, please consult a qualified lawyer.
        
        Relevant laws include:
        - Information Technology Act, 2000 (as amended)
        - Indian Penal Code, 1860
        - Sexual Harassment of Women at Workplace Act, 2013
        - Digital Personal Data Protection Act, 2023
        """


class PlatformSpecificChecker:
    """
    Platform-specific compliance for Indian context.
    """

    YOUTUBE_INDIA_RULES = {
        "age_restricted": [
            "violent",
            "graphic",
            "nude",
            "explicit",
            "drugs",
            "suicide",
            "self-harm",
            "eating disorders",
        ],
        "community_guideline_violations": [
            "hate speech",
            "harassment",
            "dangerous content",
            "misinformation",
            "spam",
        ],
        "india_specific": [
            "religious harmony",
            "caste discrimination",
            "communal content",
            "defamation",
        ],
    }

    @classmethod
    def check_youtube(cls, content: str) -> Dict:
        """Check content against YouTube India policies."""
        content_lower = content.lower()

        violations = []
        recommendations = []

        # Check age restriction triggers
        for trigger in cls.YOUTUBE_INDIA_RULES["age_restricted"]:
            if trigger in content_lower:
                violations.append(f"Age-restricted content: {trigger}")
                recommendations.append(
                    f"Consider marking video as age-restricted for '{trigger}' content"
                )

        # Check community guidelines
        for violation in cls.YOUTUBE_INDIA_RULES["community_guideline_violations"]:
            if violation in content_lower:
                violations.append(f"Community guideline concern: {violation}")

        # India-specific concerns
        india_issues = []
        for issue in cls.YOUTUBE_INDIA_RULES["india_specific"]:
            if issue in content_lower:
                india_issues.append(issue)

        if india_issues:
            violations.append(f"India-specific concerns: {', '.join(india_issues)}")
            recommendations.append(
                "Ensure content maintains religious harmony and avoids defamation"
            )

        return {
            "platform": "YouTube",
            "violations": violations,
            "recommendations": recommendations,
            "likely_monitized": len(violations) == 0,
            "may_be_restricted": len(violations) > 0,
        }

    @classmethod
    def check_instagram(cls, content: str) -> Dict:
        """Check content against Instagram community guidelines."""
        content_lower = content.lower()

        violations = []

        instagram_triggers = [
            "nude",
            "explicit",
            "violence",
            "bullying",
            "hate speech",
            "spam",
            "misinformation",
        ]

        for trigger in instagram_triggers:
            if trigger in content_lower:
                violations.append(f"Potential violation: {trigger}")

        return {
            "platform": "Instagram",
            "violations": violations,
            "may_be_removed": len(violations) > 0,
        }
