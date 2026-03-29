"""
Safety Report Generator
Creates comprehensive reports from analysis results
"""

from dataclasses import dataclass
from typing import Dict, List, Optional
from datetime import datetime
import json


@dataclass
class SafetyBadge:
    text: str
    color: str
    icon: str

    def to_html(self) -> str:
        return f"""
        <div style="
            display: inline-flex;
            align-items: center;
            gap: 8px;
            padding: 12px 24px;
            background: {self.color}15;
            border: 2px solid {self.color};
            border-radius: 30px;
            font-family: 'Segoe UI', sans-serif;
        ">
            <span style="font-size: 24px;">{self.icon}</span>
            <span style="color: {self.color}; font-weight: 700; font-size: 16px;">
                {self.text}
            </span>
        </div>
        """


class SafetyReport:
    """
    Generates comprehensive safety reports.
    """

    def __init__(self):
        self.generated_at = datetime.now().isoformat()

    def generate(
        self,
        video_info: Dict,
        analysis_results: Dict,
        checklist_results: Dict = None,
        compliance_results: Dict = None,
        scorer_results: Dict = None,
    ) -> Dict:
        """Generate full safety report."""

        # Create badge based on overall verdict
        if scorer_results:
            verdict = scorer_results.get("verdict", "UNKNOWN")
            color = scorer_results.get("overall_color", "#6b7280")
        else:
            verdict = "NOT ANALYZED"
            color = "#6b7280"

        badge = self._create_badge(verdict, color)

        # Compile all findings
        critical_findings = []
        warnings = []
        recommendations = []

        # Extract from analysis
        if analysis_results:
            for category, result in analysis_results.items():
                if isinstance(result, dict):
                    if result.get("risk_level") in ["high", "critical"]:
                        critical_findings.append(
                            {
                                "category": category,
                                "score": result.get("score", 0),
                                "findings": result.get("findings", []),
                            }
                        )
                    elif result.get("risk_level") == "medium":
                        warnings.append(
                            {
                                "category": category,
                                "findings": result.get("findings", []),
                            }
                        )

                    # Collect all recommendations
                    for rec in result.get("recommendations", []):
                        if rec not in recommendations:
                            recommendations.append(rec)

        # Extract from checklist
        if checklist_results:
            for issue in checklist_results.get("critical_issues", []):
                critical_findings.append({"category": "women_safety", "finding": issue})
            for rec in checklist_results.get("recommendations", []):
                if rec not in recommendations:
                    recommendations.append(rec)

        # Extract from compliance
        if compliance_results:
            for violation in compliance_results.get("violations", []):
                if violation.get("severity") == "criminal":
                    critical_findings.append(
                        {
                            "category": "legal",
                            "finding": f"Potential legal issue: {violation.get('section')}",
                        }
                    )
                else:
                    warnings.append(
                        {
                            "category": "legal",
                            "finding": f"Compliance concern: {violation.get('section')}",
                        }
                    )

        return {
            "report_info": {
                "generated_at": self.generated_at,
                "video_title": video_info.get("title", "Untitled"),
                "video_id": video_info.get("id", "unknown"),
            },
            "badge": badge.__dict__,
            "verdict": verdict,
            "scores": {
                "overall": scorer_results,
                "analysis": analysis_results,
                "checklist": checklist_results,
                "compliance": compliance_results,
            },
            "critical_findings": critical_findings,
            "warnings": warnings,
            "recommendations": recommendations,
            "can_post": scorer_results.get("can_post", False)
            if scorer_results
            else False,
            "do_not_post": scorer_results.get("do_not_post", False)
            if scorer_results
            else False,
            "summary": self._generate_summary(
                verdict, len(critical_findings), len(warnings), len(recommendations)
            ),
        }

    def _create_badge(self, verdict: str, color: str) -> SafetyBadge:
        """Create appropriate badge for verdict."""

        badge_info = {
            "SAFE TO POST": ("SAFE TO POST", "#22c55e", "✓"),
            "MOSTLY SAFE": ("MOSTLY SAFE", "#84cc16", "✓"),
            "REVIEW RECOMMENDED": ("REVIEW RECOMMENDED", "#eab308", "⚠"),
            "REVIEW NEEDED": ("REVIEW NEEDED", "#f97316", "⚠"),
            "REVISIONS NEEDED": ("REVISIONS NEEDED", "#f97316", "⚡"),
            "DO NOT POST": ("DO NOT POST", "#ef4444", "✗"),
            "NON-COMPLIANT": ("NON-COMPLIANT", "#ef4444", "✗"),
            "COMPLIANT": ("COMPLIANT", "#22c55e", "✓"),
            "PARTIAL COMPLIANCE": ("PARTIAL COMPLIANCE", "#f97316", "⚠"),
            "UNKNOWN": ("NOT ANALYZED", "#6b7280", "?"),
        }

        info = badge_info.get(verdict, badge_info["UNKNOWN"])
        return SafetyBadge(text=info[0], color=info[1], icon=info[2])

    def _generate_summary(
        self, verdict: str, critical_count: int, warning_count: int, rec_count: int
    ) -> str:
        """Generate human-readable summary."""

        if verdict in ["SAFE TO POST", "COMPLIANT"]:
            return (
                f"Your content appears safe to post. No critical issues detected. "
                f"We found {warning_count} minor items to be aware of."
            )
        elif verdict in ["REVIEW RECOMMENDED", "MOSTLY SAFE"]:
            return (
                f"We recommend reviewing your content before posting. "
                f"Found {critical_count} critical issue(s) and {warning_count} warning(s). "
                f"Please address the recommendations provided."
            )
        elif verdict in ["REVISIONS NEEDED", "PARTIAL COMPLIANCE"]:
            return (
                f"Your content needs revisions before posting. "
                f"Found {critical_count} critical issue(s) that must be addressed. "
                f"We recommend making changes and re-analyzing."
            )
        elif verdict in ["DO NOT POST", "NON-COMPLIANT"]:
            return (
                f"CRITICAL: We do not recommend posting this content. "
                f"Found {critical_count} critical issue(s) that could cause serious harm "
                f"or legal consequences. Please revise or consult a professional."
            )
        else:
            return "Please complete the full analysis for a detailed report."

    def to_json(self, report: Dict) -> str:
        """Export report as JSON."""
        return json.dumps(report, indent=2)

    def to_html_report(self, report: Dict) -> str:
        """Generate HTML report for embedding."""
        badge_html = self._create_badge(
            report.get("verdict", "UNKNOWN"),
            report.get("scores", {}).get("overall", {}).get("overall_color", "#6b7280"),
        ).to_html()

        html = f"""
        <!DOCTYPE html>
        <html>
        <head>
            <meta charset="UTF-8">
            <title>Content Safety Report - {report["report_info"]["video_title"]}</title>
            <style>
                body {{ 
                    font-family: 'Segoe UI', sans-serif; 
                    max-width: 800px; 
                    margin: 40px auto; 
                    padding: 20px;
                    background: #0f172a;
                    color: #e2e8f0;
                }}
                .badge {{ text-align: center; margin: 30px 0; }}
                .section {{ 
                    background: #1e293b; 
                    padding: 20px; 
                    border-radius: 12px; 
                    margin: 20px 0;
                }}
                .critical {{ border-left: 4px solid #ef4444; }}
                .warning {{ border-left: 4px solid #f97316; }}
                .recommendation {{ border-left: 4px solid #22c55e; }}
                h2 {{ color: #f8fafc; }}
                .finding {{ padding: 10px; margin: 5px 0; background: #334155; border-radius: 6px; }}
                .summary {{ font-size: 18px; line-height: 1.6; }}
            </style>
        </head>
        <body>
            <h1>Content Safety Report</h1>
            <p>Video: {report["report_info"]["video_title"]}</p>
            <p>Generated: {report["report_info"]["generated_at"]}</p>
            
            <div class="badge section">
                {badge_html}
            </div>
            
            <div class="section summary">
                <h2>Summary</h2>
                <p>{report.get("summary", "")}</p>
            </div>
            
            {"".join(f'<div class="section critical"><h2>⚠ Critical Issues ({len(report.get("critical_findings", []))})</h2>' + "".join(f'<div class="finding">{c.get("category", "").replace("_", " ").title()}: {c.get("finding", "")}</div>' for c in report.get("critical_findings", [])) + "</div>") if report.get("critical_findings") else ""}
            
            {"".join(f'<div class="section warning"><h2>⚡ Warnings ({len(report.get("warnings", []))})</h2>' + "".join(f'<div class="finding">{w.get("category", "").replace("_", " ").title()}: {w.get("finding", "")}</div>' for w in report.get("warnings", [])) + "</div>") if report.get("warnings") else ""}
            
            {"".join(f'<div class="section recommendation"><h2>✓ Recommendations</h2><ul>' + "".join(f"<li>{r}</li>" for r in report.get("recommendations", [])) + "</ul></div>") if report.get("recommendations") else ""}
            
            <div class="section">
                <p style="color: #94a3b8; font-size: 12px;">
                    This report is for guidance only and does not constitute legal advice.
                    Generated by Safecrate - Content Safety Validator
                </p>
            </div>
        </body>
        </html>
        """
        return html


class QuickReport:
    """Generate quick, simple reports."""

    @staticmethod
    def generate(
        video_title: str, score: float, verdict: str, concerns: List[str]
    ) -> str:
        """Generate a simple text report."""
        lines = [
            "=" * 50,
            "CONTENT SAFETY REPORT",
            "=" * 50,
            f"Video: {video_title}",
            f"Date: {datetime.now().strftime('%Y-%m-%d %H:%M')}",
            "",
            f"VERDICT: {verdict}",
            f"Overall Score: {score}%",
            "",
            "CONCERNS:",
        ]

        for i, concern in enumerate(concerns, 1):
            lines.append(f"  {i}. {concern}")

        lines.extend(["", "=" * 50, "Generated by Safecrate"])

        return "\n".join(lines)
