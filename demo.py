"""
Safecrate - Content Safety Validator Demo
Run this to test the analysis engine
"""

from safecrate import (
    ContentAnalyzer,
    WomenSafetyChecker,
    SensitivityScorer,
    QuickScorer,
    IndianLawChecker,
    SafetyReport,
    VideoMetadata,
)
from safecrate.safety_checklist import QuickSafetyQuiz


def demo_analysis():
    """Run a demo analysis."""

    print("=" * 60)
    print("SAFECRATE - Content Safety Validator Demo")
    print("=" * 60)
    print()

    # Sample video metadata
    video = VideoMetadata(
        title="Girls React to Viral Trend - EPIC FAIL",
        description="""
        In this video, we surprised our college friends with the latest viral challenge!
        Watch them try the dare challenge and see their hilarious reactions.
        Don't forget to like and subscribe!
        
        Tags: #viral #challenge #prank #girls #college #funny
        """,
        tags=["viral", "challenge", "prank", "girls", "college", "funny"],
        duration_seconds=600,
    )

    # Initialize components
    analyzer = ContentAnalyzer()
    checklist = WomenSafetyChecker()
    scorer = SensitivityScorer()
    compliance = IndianLawChecker()
    report_gen = SafetyReport()

    print("Analyzing content...")
    print()

    # Run analysis
    analysis_results = analyzer.analyze(metadata=video)

    # Run checklist
    # Simulating answers to checklist
    checklist_answers = {
        "consent_1": True,
        "consent_3": True,
        "portrayal_1": True,
        "portrayal_4": False,  # Hidden camera issue
        "language_1": False,
        "context_1": False,
    }
    checklist_results = checklist.run_checklist(checklist_answers)

    # Check compliance
    compliance_results = compliance.check_compliance(
        title=video.title, description=video.description, tags=video.tags
    )

    # Calculate overall score
    score_results = scorer.calculate_score(analysis_results, checklist_results)

    # Generate report
    report = report_gen.generate(
        video_info={"title": video.title, "id": "demo123"},
        analysis_results=analysis_results,
        checklist_results=checklist_results,
        compliance_results=compliance_results,
        scorer_results=score_results,
    )

    # Print results
    print("ANALYSIS RESULTS")
    print("-" * 40)

    for category, result in analysis_results.items():
        if isinstance(result, dict):
            risk = result.get("risk_level", "unknown").upper()
            score = result.get("score", 0) * 100
            print(
                f"  {category.replace('_', ' ').title():30s} {risk:10s} ({score:.0f}%)"
            )

    print()
    print("OVERALL ASSESSMENT")
    print("-" * 40)
    print(f"  Verdict: {report['verdict']}")
    print(f"  Score: {score_results['overall_score']:.0f}%")
    print()

    if report["critical_findings"]:
        print("⚠ CRITICAL ISSUES:")
        for finding in report["critical_findings"]:
            print(
                f"  - {finding.get('category', 'Unknown')}: {finding.get('findings', [''])[0] if finding.get('findings') else 'Issue detected'}"
            )
    print()

    if report["warnings"]:
        print("⚡ WARNINGS:")
        for warning in report["warnings"]:
            print(
                f"  - {warning.get('category', 'Unknown')}: {warning.get('findings', [''])[0] if warning.get('findings') else 'Review recommended'}"
            )
    print()

    if report["recommendations"]:
        print("[*] RECOMMENDATIONS:")
        for rec in report["recommendations"][:5]:
            print(f"  - {rec}")
    print()

    print("LEGAL COMPLIANCE")
    print("-" * 40)
    print(f"  Status: {compliance_results['verdict']}")
    print(f"  Score: {compliance_results['compliance_score']:.0f}%")
    if compliance_results["violations"]:
        print("  Violations:")
        for v in compliance_results["violations"]:
            print(f"    - {v['section']}: {v['description']}")
    print()

    print("=" * 60)
    print(f"CAN POST: {'YES' if report['can_post'] else 'NO'}")
    print("=" * 60)


def demo_quick_check():
    """Run a quick safety quiz."""

    print()
    print("QUICK SAFETY QUIZ")
    print("-" * 40)

    # Simulate quiz answers
    quiz_answers = {
        "q1": True,  # Consent given
        "q2": True,  # Respectful
        "q3": False,  # No hidden camera
        "q4": False,  # No derogatory language
        "q5": False,  # Can't be used for stalking
        "q6": False,  # No unsafe situations
        "q7": False,  # No personal info
        "q8": False,  # No violence normalization
        "q9": False,  # No body shaming
        "q10": True,  # Would be comfortable
    }

    verdict = QuickSafetyQuiz.get_verdict(quiz_answers)

    print(f"Quick Score: {verdict['score']:.0f}%")
    print(f"Verdict: {verdict['verdict']}")
    print(f"Critical Fails: {verdict['critical_fails']}")
    print(f"Message: {verdict['message']}")


def demo_risk_check():
    """Quick risk check for video info."""

    print()
    print("QUICK RISK CHECK")
    print("-" * 40)

    scorer = SensitivityScorer()

    # Test various video titles
    videos = [
        {
            "title": "My Morning Routine 2024",
            "description": "Sharing my daily routine",
            "tags": ["vlog", "routine", "lifestyle"],
        },
        {
            "title": "POV: Girl walks alone at night PRANK",
            "description": "We pranked girls with scary scenarios",
            "tags": ["prank", "girls", "scary", "reaction"],
        },
        {
            "title": "How to Make Money Online - Fake Method",
            "description": "This is totally fake and won't work",
            "tags": ["scam", "fake", "satire"],
        },
    ]

    for video in videos:
        result = QuickScorer.score_video(video)
        print(f"\n{video['title']}")
        print(f"  Score: {result['quick_score']}% - {result['verdict']}")
        if result["concerns"]:
            print(f"  Concerns: {', '.join(result['concerns'])}")


if __name__ == "__main__":
    demo_analysis()
    demo_quick_check()
    demo_risk_check()
