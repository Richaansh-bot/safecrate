"""
Safecrate - YouTube Link Analyzer Demo
Analyze YouTube videos directly from URLs
"""

import sys
import os

# Add parent directory to path
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from safecrate.youtube import analyze_youtube_video, full_youtube_analysis


def demo():
    print("=" * 60)
    print("SAFECRATE - YouTube Video Analyzer")
    print("=" * 60)
    print()

    # Example YouTube URLs to test
    test_urls = [
        # Replace with actual URLs or use any YouTube video
        "https://www.youtube.com/watch?v=dQw4w9WgXcQ",  # Rick Astley (placeholder)
    ]

    print("Enter a YouTube URL to analyze (or press Enter to use sample):")
    user_url = input().strip()

    if not user_url:
        print("\nUsing sample analysis...")
        # Simulate with mock data
        print("\n" + "=" * 60)
        print("ANALYSIS RESULT")
        print("=" * 60)
        print("\nVideo: Sample YouTube Video")
        print("URL: https://youtube.com/watch?v=sample")
        print("\n" + "-" * 40)
        print("QUICK SAFETY CHECK")
        print("-" * 40)
        print("Risk Score: 45%")
        print("Verdict: CAUTION")
        print("\nDetected Keywords: ['viral', 'challenge']")
        print("\nRecommendation: Review content before posting")
        return

    print(f"\nAnalyzing: {user_url}")
    print("-" * 40)

    result = analyze_youtube_video(user_url)

    if not result.get("success"):
        print(f"Error: {result.get('error', 'Unknown error')}")
        return

    video = result["video"]
    check = result["quick_check"]

    print("\n" + "=" * 60)
    print("VIDEO INFORMATION")
    print("=" * 60)
    print(f"Title: {video.get('title', 'N/A')}")
    print(f"Channel: {video.get('uploader', 'N/A')}")
    print(f"Duration: {video.get('duration', 0) // 60} min")
    print(f"Views: {video.get('view_count', 0):,}")
    print(f"Tags: {', '.join(video.get('tags', [])[:5])}")
    print(f"URL: {video.get('url', 'N/A')}")

    print("\n" + "-" * 40)
    print("SAFETY ANALYSIS")
    print("-" * 40)
    print(f"Risk Score: {check['risk_score'] * 100:.0f}%")
    print(f"Verdict: {check['verdict']}")

    if check.get("detected_keywords"):
        print(f"\nKeywords Detected: {', '.join(check['detected_keywords'])}")

    print(f"\nRecommendation: {check.get('recommendation', 'N/A')}")

    print("\n" + "=" * 60)
    print(f"Embed URL: {result.get('embed_url', 'N/A')}")
    print("=" * 60)


if __name__ == "__main__":
    demo()
