"""
Women's Safety Checklist - Special focus for Indian context
Helps content creators ensure their content is safe for women
"""

from dataclasses import dataclass, field
from typing import List, Dict
from enum import Enum


class ChecklistCategory(Enum):
    CONSENT = "consent"
    PORTRAYAL = "portrayal"
    PRIVACY = "privacy"
    LANGUAGE = "language"
    CONTEXT = "context"
    SAFETY = "safety"


@dataclass
class ChecklistItem:
    id: str
    question: str
    category: ChecklistCategory
    weight: float = 1.0
    is_critical: bool = False


class WomenSafetyChecker:
    """
    Comprehensive checklist for women's safety in content.
    Based on IT Rules 2021 and community guidelines.
    """

    def __init__(self):
        self.checklist = self._build_checklist()

    def _build_checklist(self) -> List[ChecklistItem]:
        return [
            # CONSENT
            ChecklistItem(
                id="consent_1",
                question="Have all women appearing in the video given explicit written consent?",
                category=ChecklistCategory.CONSENT,
                weight=2.0,
                is_critical=True,
            ),
            ChecklistItem(
                id="consent_2",
                question="Is the content filmed in a public place with natural foot traffic?",
                category=ChecklistCategory.CONSENT,
                weight=1.0,
            ),
            ChecklistItem(
                id="consent_3",
                question="Have you blurred/removed identifying information of individuals who didn't consent to filming?",
                category=ChecklistCategory.CONSENT,
                weight=1.5,
                is_critical=True,
            ),
            # PORTRAYAL
            ChecklistItem(
                id="portrayal_1",
                question="Does the content portray women with dignity and respect?",
                category=ChecklistCategory.PORTRAYAL,
                weight=2.0,
                is_critical=True,
            ),
            ChecklistItem(
                id="portrayal_2",
                question="Is the video avoiding stereotypical or degrading portrayals of women?",
                category=ChecklistCategory.PORTRAYAL,
                weight=1.5,
            ),
            ChecklistItem(
                id="portrayal_3",
                question="Does the content show women in empowering roles (optional for positive impact)?",
                category=ChecklistCategory.PORTRAYAL,
                weight=0.5,
            ),
            ChecklistItem(
                id="portrayal_4",
                question="Is there any voyeuristic framing or unnecessary objectification?",
                category=ChecklistCategory.PORTRAYAL,
                weight=2.0,
                is_critical=True,
            ),
            ChecklistItem(
                id="portrayal_5",
                question="Does the content avoid body shaming (any body type)?",
                category=ChecklistCategory.PORTRAYAL,
                weight=1.5,
                is_critical=True,
            ),
            # PRIVACY
            ChecklistItem(
                id="privacy_1",
                question="Are private spaces (bathrooms, bedrooms, changing areas) shown without consent?",
                category=ChecklistCategory.PRIVACY,
                weight=2.0,
                is_critical=True,
            ),
            ChecklistItem(
                id="privacy_2",
                question="Are personal details (address, phone, workplace) visible?",
                category=ChecklistCategory.PRIVACY,
                weight=2.0,
                is_critical=True,
            ),
            ChecklistItem(
                id="privacy_3",
                question="Is someone shown in a vulnerable moment (sleeping, changing, distressed)?",
                category=ChecklistCategory.PRIVACY,
                weight=2.0,
                is_critical=True,
            ),
            ChecklistItem(
                id="privacy_4",
                question="Could the content enable stalking, harassment, or harm to women shown?",
                category=ChecklistCategory.PRIVACY,
                weight=2.0,
                is_critical=True,
            ),
            # LANGUAGE
            ChecklistItem(
                id="language_1",
                question="Does the content use derogatory language toward women?",
                category=ChecklistCategory.LANGUAGE,
                weight=2.0,
                is_critical=True,
            ),
            ChecklistItem(
                id="language_2",
                question="Are sexist jokes, slurs, or derogatory terms used?",
                category=ChecklistCategory.LANGUAGE,
                weight=2.0,
                is_critical=True,
            ),
            ChecklistItem(
                id="language_3",
                question="Is the language empowering or neutral regarding gender?",
                category=ChecklistCategory.LANGUAGE,
                weight=1.0,
            ),
            # CONTEXT
            ChecklistItem(
                id="context_1",
                question="Does the content glorify or normalize harassment?",
                category=ChecklistCategory.CONTEXT,
                weight=2.0,
                is_critical=True,
            ),
            ChecklistItem(
                id="context_2",
                question="Could the content be misused to harass, intimidate, or threaten women?",
                category=ChecklistCategory.CONTEXT,
                weight=2.0,
                is_critical=True,
            ),
            ChecklistItem(
                id="context_3",
                question="Does the content encourage harmful behavior toward women?",
                category=ChecklistCategory.CONTEXT,
                weight=2.0,
                is_critical=True,
            ),
            ChecklistItem(
                id="context_4",
                question="Is it educational content about women's safety (positive context)?",
                category=ChecklistCategory.CONTEXT,
                weight=0.0,  # This is positive, reduces risk
            ),
            # SAFETY
            ChecklistItem(
                id="safety_1",
                question="Does the content show or encourage unsafe situations for women?",
                category=ChecklistCategory.SAFETY,
                weight=2.0,
                is_critical=True,
            ),
            ChecklistItem(
                id="safety_2",
                question="Could the content make women viewers feel unsafe or anxious?",
                category=ChecklistCategory.SAFETY,
                weight=1.5,
            ),
            ChecklistItem(
                id="safety_3",
                question="Does the content reveal safety vulnerabilities (daily routines, alone patterns)?",
                category=ChecklistCategory.SAFETY,
                weight=2.0,
                is_critical=True,
            ),
            ChecklistItem(
                id="safety_4",
                question="Is there appropriate content warning for sensitive topics?",
                category=ChecklistCategory.SAFETY,
                weight=1.0,
            ),
        ]

    def run_checklist(self, answers: Dict[str, bool]) -> Dict:
        """
        Run the checklist with user answers.
        Returns detailed report.
        """
        results = {
            "total_items": len(self.checklist),
            "answered_items": len(answers),
            "categories": {},
            "critical_issues": [],
            "warnings": [],
            "passed": True,
            "score": 0.0,
            "recommendations": [],
        }

        total_weight = 0
        earned_weight = 0

        # Group by category
        for category in ChecklistCategory:
            results["categories"][category.value] = {
                "items": [],
                "score": 0,
                "max_score": 0,
            }

        for item in self.checklist:
            category_data = results["categories"][item.category.value]
            item_result = {
                "id": item.id,
                "question": item.question,
                "answered": item.id in answers,
                "passed": answers.get(item.id, None),
                "is_critical": item.is_critical,
            }

            if item.id in answers:
                category_data["items"].append(item_result)
                category_data["max_score"] += item.weight
                total_weight += item.weight

                # For questions asking "Is there any X?" - if answered YES, it's a FAIL
                # For questions asking "Is there NO X?" - if answered NO, it's a FAIL
                if item.id in [
                    "portrayal_4",
                    "privacy_1",
                    "privacy_2",
                    "privacy_3",
                    "privacy_4",
                    "language_1",
                    "language_2",
                    "context_1",
                    "context_2",
                    "context_3",
                    "safety_1",
                    "safety_3",
                ]:
                    # These are "is there negative content" questions
                    # If TRUE, it's bad (passed=False means content is safe)
                    if answers[item.id] is True:
                        item_result["passed"] = False
                        results["passed"] = False
                        if item.is_critical:
                            results["critical_issues"].append(item.question)
                        else:
                            results["warnings"].append(item.question)
                    else:
                        earned_weight += item.weight
                        item_result["passed"] = True
                else:
                    # These are "do you have consent?" questions
                    # If TRUE, it's good
                    if answers[item.id] is True:
                        earned_weight += item.weight
                        item_result["passed"] = True
                    else:
                        item_result["passed"] = False
                        results["passed"] = False
                        if item.is_critical:
                            results["critical_issues"].append(item.question)
                        else:
                            results["warnings"].append(item.question)

            if item_result.get("passed") is True and item.id in answers:
                category_data["score"] = (category_data.get("score") or 0) + item.weight

        # Calculate scores
        results["score"] = (
            (earned_weight / total_weight * 100) if total_weight > 0 else 0
        )

        for category in results["categories"]:
            cat = results["categories"][category]
            if cat["max_score"] > 0:
                cat["score"] = (cat["score"] / cat["max_score"]) * 100

        # Generate recommendations
        if results["critical_issues"]:
            results["recommendations"].append(
                "CRITICAL: Address all critical issues before posting"
            )
        if results["warnings"]:
            results["recommendations"].append(
                "Review warning items to improve content safety"
            )
        if results["score"] < 80:
            results["recommendations"].append(
                "Consider having a woman friend review the content"
            )
        if results["score"] >= 90:
            results["recommendations"].append(
                "Content appears safe from women's safety perspective"
            )

        return results


class QuickSafetyQuiz:
    """
    Quick quiz to assess content safety for women.
    10 essential questions.
    """

    QUESTIONS = [
        {
            "id": "q1",
            "question": "Do all women in your video know they are being filmed and have they consented?",
            "type": "yes_no",
            "critical": True,
        },
        {
            "id": "q2",
            "question": "Does your video show women in a respectful manner?",
            "type": "yes_no",
            "critical": True,
        },
        {
            "id": "q3",
            "question": "Is there any hidden camera or voyeuristic footage of women?",
            "type": "yes_no",
            "critical": True,
            "reverse": True,  # If YES, it's bad
        },
        {
            "id": "q4",
            "question": "Does your video use derogatory language toward women?",
            "type": "yes_no",
            "critical": True,
            "reverse": True,
        },
        {
            "id": "q5",
            "question": "Could someone use this video to harass or stalk women shown?",
            "type": "yes_no",
            "critical": True,
            "reverse": True,
        },
        {
            "id": "q6",
            "question": "Does the video show women in dangerous or unsafe situations?",
            "type": "yes_no",
            "critical": True,
            "reverse": True,
        },
        {
            "id": "q7",
            "question": "Is personal information (address, workplace) visible in the video?",
            "type": "yes_no",
            "critical": True,
            "reverse": True,
        },
        {
            "id": "q8",
            "question": "Does your content normalize or glorify violence against women?",
            "type": "yes_no",
            "critical": True,
            "reverse": True,
        },
        {
            "id": "q9",
            "question": "Is there body shaming of any kind in the video?",
            "type": "yes_no",
            "critical": True,
            "reverse": True,
        },
        {
            "id": "q10",
            "question": "Would you be comfortable if your sister/daughter/mother saw this video?",
            "type": "yes_no",
        },
    ]

    @classmethod
    def get_verdict(cls, answers: Dict[str, bool]) -> Dict:
        """Calculate quick safety verdict."""
        critical_fails = 0
        total_questions = len(cls.QUESTIONS)
        passed = 0

        for q in cls.QUESTIONS:
            if q["id"] not in answers:
                continue

            answer = answers[q["id"]]

            if q.get("reverse"):
                # Reverse question: YES is bad, NO is good
                if not answer:  # NO (meaning no negative content)
                    passed += 1
                else:
                    if q.get("critical"):
                        critical_fails += 1
            else:
                # Normal question: YES is good
                if answer:
                    passed += 1
                else:
                    if q.get("critical"):
                        critical_fails += 1

        score = (passed / total_questions) * 100

        if critical_fails >= 3 or score < 50:
            verdict = "NOT SAFE"
            color = "#ef4444"  # Red
        elif critical_fails >= 1 or score < 70:
            verdict = "REVIEW NEEDED"
            color = "#f97316"  # Orange
        elif score < 85:
            verdict = "MOSTLY SAFE"
            color = "#eab308"  # Yellow
        else:
            verdict = "SAFE TO POST"
            color = "#22c55e"  # Green

        return {
            "score": score,
            "passed": passed,
            "total": total_questions,
            "critical_fails": critical_fails,
            "verdict": verdict,
            "color": color,
            "message": cls._get_message(verdict, critical_fails),
        }

    @classmethod
    def _get_message(cls, verdict: str, critical_fails: int) -> str:
        messages = {
            "NOT SAFE": "Your content has significant safety issues, especially for women. We strongly recommend NOT posting without major revisions. Critical issues found: "
            + str(critical_fails),
            "REVIEW NEEDED": "Your content needs review before posting. Please address the critical issues identified.",
            "MOSTLY SAFE": "Your content is mostly safe but could benefit from minor improvements.",
            "SAFE TO POST": "Your content appears safe from women's safety perspective. Always use your best judgment.",
        }
        return messages.get(verdict, "")
