"""
Safecrate API Server
FastAPI backend for real-time YouTube content analysis
"""

import os
import asyncio
from pathlib import Path
from typing import Optional
from datetime import datetime

from fastapi import FastAPI, HTTPException, BackgroundTasks
from fastapi.middleware.cors import CORSMiddleware
from fastapi.staticfiles import StaticFiles
from fastapi.responses import FileResponse
from pydantic import BaseModel, HttpUrl
import httpx

# Try to import optional dependencies
try:
    import yt_dlp

    YT_DLP_AVAILABLE = True
except ImportError:
    YT_DLP_AVAILABLE = False
    print("Warning: yt-dlp not installed. Using fallback mode.")

# Import analysis modules
import sys

sys.path.insert(0, str(Path(__file__).parent))
from safecrate.analyzer import ContentAnalyzer, VideoMetadata
from safecrate.scorer import SensitivityScorer
from safecrate.safety_checklist import QuickSafetyQuiz
from safecrate.compliance import IndianLawChecker

# Initialize FastAPI
app = FastAPI(
    title="Safecrate API",
    description="Content Safety Validator for Indian Content Creators",
    version="1.0.0",
)

# CORS for frontend
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Initialize analyzers
analyzer = ContentAnalyzer()
scorer = SensitivityScorer()
compliance_checker = IndianLawChecker()

# Store for analysis results (in production, use Redis or database)
analysis_results = {}


class YouTubeAnalysisRequest(BaseModel):
    url: str


class VideoAnalysisRequest(BaseModel):
    title: str
    description: str = ""
    tags: list[str] = []
    transcript: str = ""


class AnalysisResponse(BaseModel):
    success: bool
    video_id: Optional[str] = None
    title: Optional[str] = None
    channel: Optional[str] = None
    description: Optional[str] = None
    thumbnail: Optional[str] = None
    duration: Optional[int] = None
    views: Optional[int] = None
    tags: list[str] = []
    analysis: Optional[dict] = None
    quick_check: Optional[dict] = None
    verdict: str = ""
    risk_score: float = 0.0
    message: str = ""
    error: Optional[str] = None


def extract_youtube_id(url: str) -> Optional[str]:
    """Extract video ID from various YouTube URL formats."""
    import re

    patterns = [
        r"(?:youtube\.com/watch\?v=|youtu\.be/|youtube\.com/embed/)([a-zA-Z0-9_-]{11})",
        r"youtube\.com/shorts/([a-zA-Z0-9_-]{11})",
        r"youtube\.com/live/([a-zA-Z0-9_-]{11})",
    ]
    for pattern in patterns:
        match = re.search(pattern, url)
        if match:
            return match.group(1)
    return None


async def fetch_youtube_metadata(video_id: str) -> dict:
    """Fetch video metadata from YouTube oEmbed API."""
    async with httpx.AsyncClient() as client:
        try:
            # Get oEmbed data
            oembed_url = f"https://www.youtube.com/oembed?url=https://www.youtube.com/watch?v={video_id}&format=json"
            response = await client.get(oembed_url, timeout=10.0)

            if response.status_code == 200:
                data = response.json()
                return {
                    "title": data.get("title", ""),
                    "channel": data.get("author_name", ""),
                    "thumbnail": f"https://img.youtube.com/vi/{video_id}/maxresdefault.jpg",
                }
        except Exception as e:
            print(f"oEmbed error: {e}")

    return {
        "title": f"YouTube Video {video_id}",
        "channel": "Unknown",
        "thumbnail": f"https://img.youtube.com/vi/{video_id}/hqdefault.jpg",
    }


def analyze_youtube_content(title: str, description: str, tags: list) -> dict:
    """Analyze content using Safecrate analyzers."""
    # Create metadata object
    metadata = VideoMetadata(
        title=title, description=description, tags=tags, language="en"
    )

    # Run analysis
    analysis = analyzer.analyze(metadata=metadata)

    # Calculate scores
    scores = scorer.calculate_score(analysis)

    # Run compliance check
    compliance = compliance_checker.check_compliance(
        title=title, description=description, tags=tags
    )

    # Format results
    categories = {}
    for cat_key, result in analysis.items():
        if hasattr(result, "score"):
            score = result.score
            risk = (
                result.risk_level.value
                if hasattr(result.risk_level, "value")
                else str(result.risk_level)
            )
        else:
            score = result.get("score", 0)
            risk = result.get("risk_level", "safe")

        categories[cat_key] = {
            "score": score,
            "risk_level": risk,
            "findings": result.findings
            if hasattr(result, "findings")
            else result.get("findings", []),
            "recommendations": result.recommendations
            if hasattr(result, "recommendations")
            else result.get("recommendations", []),
        }

    return {
        "categories": categories,
        "overall_score": scores.get("overall_score", 0),
        "verdict": scores.get("verdict", "UNKNOWN"),
        "can_post": scores.get("can_post", False),
        "warnings": scores.get("warnings", []),
        "compliance": compliance,
    }


@app.get("/")
async def root():
    """Serve the frontend."""
    index_path = Path(__file__).parent / "frontend" / "dist" / "index.html"
    if index_path.exists():
        return FileResponse(str(index_path))
    return {"message": "Safecrate API is running. Build frontend for full UI."}


@app.post("/api/analyze/youtube", response_model=AnalysisResponse)
async def analyze_youtube(request: YouTubeAnalysisRequest):
    """Analyze a YouTube video URL."""
    try:
        # Extract video ID
        video_id = extract_youtube_id(request.url)
        if not video_id:
            return AnalysisResponse(success=False, error="Invalid YouTube URL")

        # Fetch metadata
        metadata = await fetch_youtube_metadata(video_id)

        # Simulate some common YouTube tags based on title
        title_lower = metadata["title"].lower()
        tags = []

        # Auto-detect content type from title
        risk_keywords = {
            "prank": 0.15,
            "challenge": 0.1,
            "roast": 0.2,
            "girls": 0.1,
            "college": 0.1,
            "hot": 0.15,
            "sexy": 0.25,
            "expose": 0.2,
            "leak": 0.25,
            "reaction": 0.1,
            "vlog": 0.05,
            "tutorial": 0.02,
            "music": 0.05,
            "comedy": 0.1,
            "funny": 0.05,
            "dance": 0.05,
            "food": 0.03,
            "travel": 0.03,
            "gaming": 0.05,
        }

        for keyword, weight in risk_keywords.items():
            if keyword in title_lower:
                tags.append(keyword)

        # Run analysis
        analysis = analyze_youtube_content(
            title=metadata["title"], description="", tags=tags
        )

        # Determine quick verdict
        risk_score = analysis["overall_score"] / 100
        if risk_score < 0.3:
            verdict = "LIKELY SAFE"
            color = "#22c55e"
        elif risk_score < 0.5:
            verdict = "CAUTION"
            color = "#eab308"
        else:
            verdict = "REVIEW NEEDED"
            color = "#f97316"

        return AnalysisResponse(
            success=True,
            video_id=video_id,
            title=metadata["title"],
            channel=metadata["channel"],
            thumbnail=metadata["thumbnail"],
            tags=tags,
            analysis=analysis["categories"],
            quick_check={
                "verdict": verdict,
                "color": color,
                "risk_score": risk_score,
                "recommendation": f"Content analysis shows {verdict.lower()} status.",
            },
            verdict=verdict,
            risk_score=risk_score,
            message=f"Analysis complete. Overall risk: {verdict}",
        )

    except Exception as e:
        return AnalysisResponse(success=False, error=str(e))


@app.post("/api/analyze/text", response_model=AnalysisResponse)
async def analyze_text(request: VideoAnalysisRequest):
    """Analyze video details from text input."""
    try:
        # Run analysis
        analysis = analyze_youtube_content(
            title=request.title, description=request.description, tags=request.tags
        )

        # Determine verdict
        risk_score = analysis["overall_score"] / 100
        if risk_score < 0.3:
            verdict = "LIKELY SAFE"
            color = "#22c55e"
        elif risk_score < 0.5:
            verdict = "CAUTION"
            color = "#eab308"
        else:
            verdict = "REVIEW NEEDED"
            color = "#f97316"

        return AnalysisResponse(
            success=True,
            title=request.title,
            description=request.description,
            tags=request.tags,
            analysis=analysis["categories"],
            quick_check={
                "verdict": verdict,
                "color": color,
                "risk_score": risk_score,
                "recommendation": f"Content analysis shows {verdict.lower()} status.",
            },
            verdict=verdict,
            risk_score=risk_score,
            message=f"Analysis complete. Overall risk: {verdict}",
        )

    except Exception as e:
        return AnalysisResponse(success=False, error=str(e))


@app.get("/api/health")
async def health_check():
    """Health check endpoint."""
    return {
        "status": "healthy",
        "timestamp": datetime.now().isoformat(),
        "yt_dlp_available": YT_DLP_AVAILABLE,
    }


@app.get("/api/quick-check")
async def quick_check(url: str):
    """Quick safety check for YouTube URL."""
    video_id = extract_youtube_id(url)
    if not video_id:
        return {"valid": False, "error": "Invalid URL"}

    return {
        "valid": True,
        "video_id": video_id,
        "embed_url": f"https://www.youtube.com/embed/{video_id}",
        "thumbnail_url": f"https://img.youtube.com/vi/{video_id}/hqdefault.jpg",
    }


if __name__ == "__main__":
    import uvicorn

    print("=" * 50)
    print("SAFECRATE API SERVER")
    print("=" * 50)
    print("Starting server...")
    print("API Docs: http://localhost:8000/docs")
    print("Frontend: http://localhost:8000")
    print("=" * 50)
    uvicorn.run("server:app", host="0.0.0.0", port=8000, reload=True)
