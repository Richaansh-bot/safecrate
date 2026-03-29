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
    print("[INIT] yt-dlp imported successfully")
except ImportError as e:
    YT_DLP_AVAILABLE = False
    print(f"[INIT] Warning: yt-dlp not installed. Using fallback mode. Error: {e}")

# AssemblyAI for transcription (optional)
try:
    import assemblyai as aai

    ASSEMBLYAI_AVAILABLE = True
    print("[INIT] AssemblyAI SDK imported successfully")
except ImportError as e:
    ASSEMBLYAI_AVAILABLE = False
    print(f"[INIT] AssemblyAI not installed. {e}")

# Get API key from environment or use demo
ASSEMBLYAI_API_KEY = os.environ.get("ASSEMBLYAI_API_KEY", "")
if ASSEMBLYAI_API_KEY:
    print(f"[INIT] AssemblyAI API key found")

# Whisper for local transcription (free, unlimited)
try:
    from faster_whisper import WhisperModel

    WHISPER_AVAILABLE = True
    print("[INIT] faster-whisper imported successfully")
except ImportError as e:
    WHISPER_AVAILABLE = False
    print(f"[INIT] Warning: faster-whisper not installed. {e}")

# Whisper model instance (lazy loaded)
whisper_model = None

# Transcription settings
WHISPER_MODEL_SIZE = os.environ.get(
    "WHISPER_MODEL", "tiny"
)  # tiny (~75MB, fastest), base (~140MB), small (~500MB)

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
    transcript: Optional[str] = None  # Optional manual transcript
    use_whisper: bool = False  # Opt-in for Whisper (slow on CPU)


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


def fetch_youtube_transcript(video_url: str, max_retries: int = 3) -> tuple[str, bool]:
    """
    Fetch transcript/subtitles from YouTube video using yt-dlp.
    Returns (transcript_text, success)
    """
    if not YT_DLP_AVAILABLE:
        return "", False

    transcript_text = ""
    success = False

    ydl_opts = {
        "skip_download": True,
        "quiet": True,
        "no_warnings": True,
        "writesubtitles": True,
        "writeautomaticsub": True,
        "subtitlesformat": "vtt",
    }

    for attempt in range(max_retries):
        try:
            with yt_dlp.YoutubeDL(ydl_opts) as ydl:
                # Extract info including available subtitles
                info = ydl.extract_info(video_url, download=False)

                if info:
                    # Get video description as fallback context
                    description = info.get("description", "") or ""

                    # Try to get transcript using yt-dlp's transcript functionality
                    try:
                        # Get subtitles in VTT format by downloading to memory
                        subtitles = info.get("subtitles", {}) or {}
                        auto_captions = info.get("automatic_captions", {}) or {}

                        # Combine manual and auto subtitles
                        all_subs = {**auto_captions, **subtitles}

                        if all_subs:
                            # Try to get English subtitles first, then Hindi, then any available
                            lang_codes = [
                                "en",
                                "en-US",
                                "en-GB",
                                "hi",
                                "hi-orig",
                                "mr",
                                "a.en",
                                "a.en-US",
                            ]

                            for lang in lang_codes:
                                if lang in all_subs:
                                    sub_entries = all_subs[lang]
                                    if isinstance(sub_entries, list):
                                        # Get subtitle URL with retry
                                        for entry in sub_entries:
                                            if (
                                                isinstance(entry, dict)
                                                and "url" in entry
                                            ):
                                                subtitle_url = entry["url"]
                                                try:
                                                    resp = httpx.get(
                                                        subtitle_url, timeout=20
                                                    )
                                                    if resp.status_code == 200:
                                                        vtt_content = resp.text
                                                        # Check if it's actually VTT (not an error page)
                                                        if not vtt_content.startswith(
                                                            "<!DOCTYPE"
                                                        ):
                                                            transcript_text = (
                                                                parse_vtt_to_text(
                                                                    vtt_content
                                                                )
                                                            )
                                                            if (
                                                                transcript_text
                                                                and len(transcript_text)
                                                                > 50
                                                            ):
                                                                success = True
                                                                print(
                                                                    f"[TRANSCRIPT] Fetched {lang} subtitles ({len(transcript_text)} chars)"
                                                                )
                                                                break
                                                        else:
                                                            print(
                                                                f"[TRANSCRIPT] Got error page for {lang}, trying next..."
                                                            )
                                                    elif resp.status_code == 429:
                                                        # Rate limited - wait and retry
                                                        import time

                                                        wait_time = (attempt + 1) * 2
                                                        print(
                                                            f"[TRANSCRIPT] Rate limited, waiting {wait_time}s..."
                                                        )
                                                        time.sleep(wait_time)
                                                        break  # Break inner loop to retry outer
                                                    else:
                                                        print(
                                                            f"[TRANSCRIPT] HTTP {resp.status_code} for {lang}"
                                                        )
                                                except Exception as e:
                                                    print(
                                                        f"[TRANSCRIPT] Error fetching {lang}: {e}"
                                                    )
                                                    continue
                                        if success:
                                            break
                    except Exception as e:
                        print(f"Subtitle extraction error: {e}")

                    # Include description if we have it
                    if description:
                        if transcript_text:
                            transcript_text += (
                                " [VIDEO DESCRIPTION] " + description[:2000]
                            )
                        elif (
                            attempt == max_retries - 1
                        ):  # Last attempt, use description as fallback
                            transcript_text = (
                                "[VIDEO DESCRIPTION] " + description[:2000]
                            )
                            success = True

        except Exception as e:
            print(f"yt-dlp error: {e}")

        if success:
            break

        # Wait before retry
        if attempt < max_retries - 1:
            import time

            wait = (attempt + 1) * 3
            print(f"[TRANSCRIPT] Retry {attempt + 1}/{max_retries} in {wait}s...")
            time.sleep(wait)

    return transcript_text.strip(), success


def parse_vtt_to_text(vtt_content: str) -> str:
    """Parse VTT subtitle format to plain text."""
    lines = vtt_content.split("\n")
    text_lines = []

    for line in lines:
        # Skip VTT headers and timing lines
        line = line.strip()
        if not line:
            continue
        if line.startswith("WEBVTT"):
            continue
        if "-->" in line:
            continue
        if line.startswith("NOTE"):
            continue
        if line.startswith("STYLE"):
            continue
        if line.startswith("REGION"):
            continue
        # Skip lines that are just numbers (cue identifiers)
        if line.isdigit():
            continue
        # Clean HTML tags
        import re

        line = re.sub(r"<[^>]+>", "", line)
        if line:
            text_lines.append(line)

    return " ".join(text_lines)


async def fetch_transcript_whisper(video_url: str) -> tuple[str, bool]:
    """
    Fetch transcript using local Whisper model (free, unlimited).
    Downloads audio from YouTube and transcribes using faster-whisper.
    """
    global whisper_model

    if not WHISPER_AVAILABLE:
        return "", False

    import tempfile

    transcript_text = ""
    success = False
    temp_audio_path = None

    try:
        print(f"[WHISPER] Starting transcription for: {video_url}")

        # Lazy load the Whisper model
        if whisper_model is None:
            print(
                f"[WHISPER] Loading model: {WHISPER_MODEL_SIZE} (first time, ~140MB download)"
            )
            whisper_model = WhisperModel(
                WHISPER_MODEL_SIZE,
                device="cpu",  # Use CPU (cross-platform compatible)
                compute_type="int8",  # Fast inference
            )
            print("[WHISPER] Model loaded successfully")

        # Download audio from YouTube
        print("[WHISPER] Downloading audio from YouTube...")

        ydl_opts = {
            "format": "bestaudio/best",
            "outtmpl": "%(id)s.%(ext)s",
            "quiet": True,
            "no_warnings": True,
            "postprocessors": [
                {
                    "key": "FFmpegExtractAudio",
                    "preferredcodec": "mp3",
                    "preferredquality": "192",
                }
            ],
        }

        with tempfile.TemporaryDirectory() as temp_dir:
            ydl_opts["outtmpl"] = os.path.join(temp_dir, "%(id)s.%(ext)s")

            with yt_dlp.YoutubeDL(ydl_opts) as ydl:
                info = ydl.extract_info(video_url, download=True)
                if info:
                    audio_path = ydl.prepare_filename(info)
                    # Find the mp3 file
                    mp3_path = audio_path.rsplit(".", 1)[0] + ".mp3"

                    if os.path.exists(mp3_path):
                        temp_audio_path = mp3_path
                        print(f"[WHISPER] Audio downloaded: {mp3_path}")

                        # Transcribe with Whisper (optimized for speed)
                        # Only transcribe first 60 seconds for speed
                        print(
                            "[WHISPER] Transcribing audio (first 60 seconds for speed)..."
                        )
                        segments, info = whisper_model.transcribe(
                            mp3_path,
                            language="en",  # Primary language
                            task="transcribe",
                            beam_size=1,  # Faster
                            vad_filter=False,  # Disable for speed
                            initial_prompt="This is a video that may contain speech.",
                            max_new_tokens=500,  # Limit output for speed
                        )

                        # Collect all segments
                        full_text = []
                        segment_count = 0
                        for segment in segments:
                            full_text.append(segment.text)
                            segment_count += 1
                            if segment_count % 20 == 0:
                                print(
                                    f"[WHISPER] Processed {segment_count} segments..."
                                )

                        transcript_text = " ".join(full_text)
                        success = len(transcript_text) > 0
                        print(
                            f"[WHISPER] Transcription complete: {len(transcript_text)} chars, {segment_count} segments"
                        )

    except Exception as e:
        print(f"[WHISPER] Error: {e}")
        transcript_text = ""
        success = False

    return transcript_text.strip(), success


async def fetch_transcript_assemblyai(video_url: str) -> tuple[str, bool]:
    """
    Fetch transcript using AssemblyAI API.
    AssemblyAI can directly transcribe YouTube videos.
    Returns (transcript_text, success)
    """
    if not ASSEMBLYAI_AVAILABLE:
        return "", False

    if not ASSEMBLYAI_API_KEY:
        return "", False

    try:
        import assemblyai as aai

        print(f"[ASSEMBLYAI] Starting transcription for: {video_url}")

        config = aai.TranscriptionConfig(
            audio_start_from=0,
            audio_end_at=120,  # First 2 minutes for speed
            punctuate=True,
            format_text=True,
        )

        transcriber = aai.Transcriber()
        transcript = transcriber.transcribe(
            video_url, config=config, api_key=ASSEMBLYAI_API_KEY
        )

        if transcript.status == aai.TranscriptStatus.error:
            print(f"[ASSEMBLYAI] Error: {transcript.error}")
            return "", False

        if transcript.text:
            print(f"[ASSEMBLYAI] Transcript fetched: {len(transcript.text)} chars")
            return transcript.text, True

        return "", False

    except Exception as e:
        print(f"[ASSEMBLYAI] Exception: {e}")
        return "", False


def analyze_youtube_content(
    title: str, description: str, tags: list, transcript: str = ""
) -> dict:
    """Analyze content using Safecrate analyzers."""
    # Create metadata object
    metadata = VideoMetadata(
        title=title, description=description, tags=tags, language="en"
    )

    # Prepare analysis data with transcript
    analysis_data = {"transcript": transcript} if transcript else {}

    # Run analysis
    analysis = analyzer.analyze(metadata=metadata, analysis_data=analysis_data)

    # Calculate scores
    scores = scorer.calculate_score(analysis)

    # Run compliance check
    compliance = compliance_checker.check_compliance(
        title=title, description=description, tags=tags, transcript=transcript
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
        "transcript_analyzed": bool(transcript),
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
            "roast": 0.25,
            "girls": 0.15,
            "college": 0.15,
            "hot": 0.2,
            "sexy": 0.3,
            "expose": 0.25,
            "leak": 0.3,
            "reaction": 0.1,
            "vlog": 0.05,
            "tutorial": 0.02,
            "music": 0.05,
            "comedy": 0.1,
            "stand-up": 0.15,
            "standup": 0.15,
            "comedian": 0.15,
            "funny": 0.05,
            "dance": 0.05,
            "food": 0.03,
            "travel": 0.03,
            "gaming": 0.05,
            "open mic": 0.1,
            "crowd work": 0.1,
            "crowd-work": 0.1,
            "bantai": 0.1,
            "pubg": 0.08,
            "minecraft": 0.05,
            "biology": 0.08,  # Biology class could be edgy
            "class": 0.05,
        }

        for keyword, weight in risk_keywords.items():
            if keyword in title_lower:
                tags.append(keyword)

        # Fetch transcript
        transcript = ""
        transcript_fetched = False
        transcript_source = "none"

        # 1. Use manual transcript if provided
        if request.transcript:
            transcript = request.transcript
            transcript_fetched = True
            transcript_source = "manual"
            print(f"[TRANSCRIPT] Using manual transcript: {len(transcript)} chars")

        # 2. Try Whisper only if explicitly requested (slow on CPU)
        elif request.use_whisper and WHISPER_AVAILABLE:
            print(
                f"[TRANSCRIPT] Whisper requested - this may take 1-5 minutes on CPU..."
            )
            transcript, transcript_fetched = await fetch_transcript_whisper(request.url)
            if transcript_fetched:
                transcript_source = "whisper"
                print(f"[TRANSCRIPT] Whisper success: {len(transcript)} chars")

        # 3. Try yt-dlp subtitles (may be rate limited)
        elif not transcript_fetched and YT_DLP_AVAILABLE:
            print(f"[TRANSCRIPT] Trying yt-dlp subtitles for: {request.url}")
            transcript, transcript_fetched = fetch_youtube_transcript(request.url)
            if transcript_fetched:
                transcript_source = "ytdlp"
                print(f"[TRANSCRIPT] yt-dlp success: {len(transcript)} chars")

        # 4. Fall back to AssemblyAI if available
        if not transcript_fetched and ASSEMBLYAI_AVAILABLE and ASSEMBLYAI_API_KEY:
            print(f"[TRANSCRIPT] Trying AssemblyAI for: {request.url}")
            transcript, transcript_fetched = await fetch_transcript_assemblyai(
                request.url
            )
            if transcript_fetched:
                transcript_source = "assemblyai"
                print(f"[TRANSCRIPT] AssemblyAI success: {len(transcript)} chars")

        if not transcript_fetched:
            print(
                "[TRANSCRIPT] No transcript available. Analysis based on metadata only."
            )

        # Run analysis with transcript
        analysis = analyze_youtube_content(
            title=metadata["title"], description="", tags=tags, transcript=transcript
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
        "whisper_available": WHISPER_AVAILABLE,
        "whisper_model": WHISPER_MODEL_SIZE if WHISPER_AVAILABLE else None,
        "assemblyai_available": ASSEMBLYAI_AVAILABLE,
        "assemblyai_configured": bool(ASSEMBLYAI_API_KEY),
        "subtitle_capable": YT_DLP_AVAILABLE,  # Can fetch YouTube subtitles if not rate limited
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
    print(f"yt-dlp available: {YT_DLP_AVAILABLE}")
    print("Starting server...")
    print("API Docs: http://localhost:8001/docs")
    print("Frontend: http://localhost:8001")
    print("=" * 50)
    uvicorn.run(app, host="0.0.0.0", port=8001, reload=False)
