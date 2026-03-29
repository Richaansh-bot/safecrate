# Safecrate - Content Safety Validator

A real-time content safety analysis tool for Indian content creators. Paste a YouTube link or enter video details to get instant safety analysis.

## 🚀 Quick Start

### Windows
```bash
start.bat
```

### Linux/Mac
```bash
chmod +x start.sh
./start.sh
```

### Manual Start
```bash
# Terminal 1 - API Server
pip install fastapi uvicorn httpx
python server.py

# Terminal 2 - Frontend
cd frontend
npm install
npm run dev
```

Then open **http://localhost:5173**

## Features

- **YouTube URL Analysis** - Paste any YouTube link for instant safety check
- **Text Input** - Enter video title, description, and tags for analysis
- **10 Safety Categories**:
  - 👩 Women Safety
  - ⚔️ Violence
  - 🔞 Sexual Content
  - ⚠️ Harassment
  - 🔒 Privacy
  - ⚖️ Legal Compliance (IT Act, IPC)
  - 🕌 Cultural Sensitivity
  - 💔 Self-Harm
  - ⚡ Dangerous Activities
  - 📢 Misinformation

## API Endpoints

| Endpoint | Method | Description |
|----------|--------|-------------|
| `/api/analyze/youtube` | POST | Analyze YouTube video URL |
| `/api/analyze/text` | POST | Analyze video details |
| `/api/quick-check` | GET | Validate YouTube URL |
| `/api/health` | GET | Server health check |

### Example API Usage

```bash
# Analyze YouTube video
curl -X POST http://localhost:8000/api/analyze/youtube \
  -H "Content-Type: application/json" \
  -d '{"url": "https://www.youtube.com/watch?v=..."}'

# Analyze text
curl -X POST http://localhost:8000/api/analyze/text \
  -H "Content-Type: application/json" \
  -d '{"title": "My Video", "description": "...", "tags": ["vlog"]}'
```

## For Developers

### Project Structure
```
safecrate/
├── server.py              # FastAPI backend server
├── safecrate/            # Analysis modules
│   ├── analyzer.py       # Content analysis engine
│   ├── scorer.py         # Sensitivity scoring
│   ├── compliance.py     # Indian law compliance
│   └── youtube/          # YouTube integration
├── frontend/             # React frontend
│   └── src/
│       ├── App.jsx       # Main app
│       ├── api.js        # API service
│       └── components/   # UI components
└── start.py             # Launcher script
```

### Tech Stack
- **Backend**: FastAPI, Python
- **Frontend**: React, Tailwind CSS, Framer Motion
- **Analysis**: Custom NLP-based safety scoring

## License

MIT - Built for Indian content creators with ❤️
