import { useState } from 'react'
import { motion } from 'framer-motion'

export default function YouTubeInput({ onAnalyze, isAnalyzing }) {
  const [url, setUrl] = useState('')
  const [error, setError] = useState('')

  const isValidYouTubeUrl = (url) => {
    const patterns = [
      /^(https?:\/\/)?(www\.)?youtube\.com\/watch\?v=[\w-]+/,
      /^(https?:\/\/)?(www\.)?youtu\.be\/[\w-]+/,
      /^(https?:\/\/)?(www\.)?youtube\.com\/embed\/[\w-]+/,
      /^(https?:\/\/)?(www\.)?youtube\.com\/shorts\/[\w-]+/,
    ]
    return patterns.some(pattern => pattern.test(url))
  }

  const extractVideoId = (url) => {
    const patterns = [
      /youtube\.com\/watch\?v=([\w-]+)/,
      /youtu\.be\/([\w-]+)/,
      /youtube\.com\/embed\/([\w-]+)/,
      /youtube\.com\/shorts\/([\w-]+)/,
    ]
    for (const pattern of patterns) {
      const match = url.match(pattern)
      if (match) return match[1]
    }
    return null
  }

  const handleSubmit = (e) => {
    e.preventDefault()
    
    if (!url.trim()) {
      setError('Please enter a YouTube URL')
      return
    }
    
    if (!isValidYouTubeUrl(url)) {
      setError('Please enter a valid YouTube URL')
      return
    }
    
    setError('')
    const videoId = extractVideoId(url)
    
    onAnalyze({
      type: 'youtube',
      url: url,
      videoId: videoId,
      embedUrl: `https://www.youtube.com/embed/${videoId}`
    })
  }

  return (
    <motion.div
      initial={{ opacity: 0, y: 20 }}
      animate={{ opacity: 1, y: 0 }}
      className="card p-8 mb-8"
    >
      <div className="flex items-center gap-3 mb-6">
        <div className="w-12 h-12 rounded-xl bg-red-500/20 flex items-center justify-center">
          <svg className="w-6 h-6 text-red-500" viewBox="0 0 24 24" fill="currentColor">
            <path d="M19.615 3.184c-3.604-.246-11.631-.245-15.23 0C.488 3.45.029 5.804 0 12c.029 6.185.484 8.549 4.385 8.816 3.6.245 11.626.246 15.23 0C23.512 20.55 23.971 18.196 24 12c-.029-6.185-.484-8.549-4.385-8.816zM9 16V8l8 3.993L9 16z"/>
          </svg>
        </div>
        <div>
          <h2 className="text-xl font-bold">Analyze YouTube Video</h2>
          <p className="text-sm text-secondary">Paste a YouTube link for instant safety analysis</p>
        </div>
      </div>

      <form onSubmit={handleSubmit}>
        <div className="flex gap-3">
          <div className="flex-1">
            <input
              type="text"
              className={`input ${error ? 'border-red-500' : ''}`}
              placeholder="https://www.youtube.com/watch?v=..."
              value={url}
              onChange={(e) => {
                setUrl(e.target.value)
                setError('')
              }}
            />
            {error && (
              <p className="text-red-400 text-sm mt-2">{error}</p>
            )}
          </div>
          <button
            type="submit"
            className="btn-primary px-6 flex items-center gap-2"
            disabled={isAnalyzing}
          >
            {isAnalyzing ? (
              <>
                <div className="w-5 h-5 border-2 border-white/30 border-t-white rounded-full animate-spin" />
                Analyzing
              </>
            ) : (
              <>
                <svg className="w-5 h-5" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                  <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M21 21l-6-6m2-5a7 7 0 11-14 0 7 7 0 0114 0z" />
                </svg>
                Analyze
              </>
            )}
          </button>
        </div>
      </form>

      <div className="mt-4 p-4 rounded-lg bg-white/5">
        <p className="text-xs text-secondary mb-2">Supported formats:</p>
        <div className="flex flex-wrap gap-2 text-xs text-secondary">
          <span className="px-2 py-1 bg-white/10 rounded">youtube.com/watch?v=...</span>
          <span className="px-2 py-1 bg-white/10 rounded">youtu.be/...</span>
          <span className="px-2 py-1 bg-white/10 rounded">youtube.com/shorts/...</span>
          <span className="px-2 py-1 bg-white/10 rounded">youtube.com/embed/...</span>
        </div>
      </div>
    </motion.div>
  )
}
