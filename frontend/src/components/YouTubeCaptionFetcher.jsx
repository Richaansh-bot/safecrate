import { useState } from 'react'
import { motion } from 'framer-motion'

export default function YouTubeCaptionFetcher({ onCaptionsFound, videoId, disabled }) {
  const [isLoading, setIsLoading] = useState(false)
  const [status, setStatus] = useState('')
  const [error, setError] = useState('')

  const fetchCaptions = async () => {
    if (!videoId) return
    
    setIsLoading(true)
    setStatus('Fetching captions...')
    setError('')

    try {
      // Method 1: Try YouTube's transcript API via CORS proxy
      const transcriptUrl = `https://youtubetranscript.com/?video_id=${videoId}`
      
      // Use a CORS proxy to fetch captions
      const corsProxy = 'https://corsproxy.io/?'
      const targetUrl = encodeURIComponent(`https://subtitle.tools/?url=https://www.youtube.com/watch?v=${videoId}`)
      
      // Alternative: Fetch directly from YouTube's caption endpoint
      const captionResponse = await fetch(
        `https://subtitle.tools/captions/${videoId}`,
        {
          headers: {
            'Accept': 'application/json, text/plain, */*',
            'Origin': window.location.origin,
          }
        }
      )

      if (captionResponse.ok) {
        const data = await captionResponse.json()
        if (data.text || data.captions) {
          onCaptionsFound(data.text || data.captions)
          setStatus(`Captions found (${(data.text || data.captions).length} characters)`)
          setIsLoading(false)
          return
        }
      }

      // Method 2: Direct YouTube API approach
      setStatus('Trying alternative method...')
      
      // Use YouTube's oEmbed to get video info, then fetch transcript
      const oembedUrl = `https://www.youtube.com/oembed?url=https://www.youtube.com/watch?v=${videoId}&format=json`
      const oembedResponse = await fetch(oembedUrl)
      
      if (oembedResponse.ok) {
        // Get video page and extract caption URL
        const videoPageUrl = `https://www.youtube.com/watch?v=${videoId}`
        const proxyUrl = `https://api.allorigins.win/raw?url=${encodeURIComponent(videoPageUrl)}`
        
        const pageResponse = await fetch(proxyUrl)
        if (pageResponse.ok) {
          const html = await pageResponse.text()
          
          // Look for caption track URLs in the page
          const captionMatch = html.match(/"captionTracks":\[(.*?)\]/)
          if (captionMatch) {
            try {
              const captionData = JSON.parse('[' + captionMatch[1] + ']')
              if (captionData.length > 0) {
                const captionUrl = captionData[0].baseUrl
                if (captionUrl) {
                  const captionTextResponse = await fetch(captionUrl)
                  if (captionTextResponse.ok) {
                    const vttText = await captionTextResponse.text()
                    // Parse VTT to plain text
                    const text = parseVTT(vttText)
                    if (text) {
                      onCaptionsFound(text)
                      setStatus(`Captions extracted (${text.length} characters)`)
                      setIsLoading(false)
                      return
                    }
                  }
                }
              }
            } catch (e) {
              console.log('Caption parse error:', e)
            }
          }
        }
      }

      // Method 3: Try another CORS proxy
      setStatus('Trying CORS proxy...')
      const alternativeProxy = `https://corsproxy.io/?${encodeURIComponent(`https://youtubetranscript.com/?video_id=${videoId}`)}`
      
      try {
        const proxyResponse = await fetch(alternativeProxy, { timeout: 10000 })
        if (proxyResponse.ok) {
          const html = await proxyResponse.text()
          // Parse the HTML response for transcript text
          const textMatch = html.match(/<body>([\s\S]*?)<\/body>/i)
          if (textMatch) {
            const cleanText = textMatch[1]
              .replace(/<[^>]+>/g, ' ')
              .replace(/\s+/g, ' ')
              .trim()
            
            if (cleanText.length > 50) {
              onCaptionsFound(cleanText)
              setStatus(`Captions found via proxy (${cleanText.length} characters)`)
              setIsLoading(false)
              return
            }
          }
        }
      } catch (proxyError) {
        console.log('CORS proxy error:', proxyError)
      }

      setError('No captions available for this video. Try using the Text Input tab.')
      setStatus('')
      
    } catch (err) {
      console.error('Caption fetch error:', err)
      setError('Failed to fetch captions. The video may not have captions available.')
      setStatus('')
    }

    setIsLoading(false)
  }

  const parseVTT = (vttText) => {
    const lines = vttText.split('\n')
    const textLines = []
    
    for (const line of lines) {
      const trimmed = line.trim()
      // Skip VTT headers and timing lines
      if (!trimmed) continue
      if (trimmed.startsWith('WEBVTT')) continue
      if (trimmed.startsWith('NOTE')) continue
      if (trimmed.includes('-->')) continue
      if (/^\d+$/.test(trimmed)) continue
      
      // Clean HTML tags
      const clean = trimmed.replace(/<[^>]+>/g, '')
      if (clean && clean.length > 1) {
        textLines.push(clean)
      }
    }
    
    return textLines.join(' ')
  }

  return (
    <motion.div
      initial={{ opacity: 0 }}
      animate={{ opacity: 1 }}
      className="mt-4 p-4 rounded-lg bg-emerald-500/10 border border-emerald-500/30"
    >
      <div className="flex items-center justify-between">
        <div className="flex-1">
          <p className="text-sm text-emerald-400 mb-1">
            Get Video Captions for Deeper Analysis
          </p>
          <p className="text-xs text-secondary">
            Fetches automatic captions/subtitles from YouTube for accurate content analysis
          </p>
          {status && (
            <p className="text-xs text-emerald-300 mt-2">{status}</p>
          )}
          {error && (
            <p className="text-xs text-amber-400 mt-2">{error}</p>
          )}
        </div>
        
        <button
          onClick={fetchCaptions}
          disabled={isLoading || disabled}
          className={`ml-4 px-4 py-2 rounded-lg text-sm font-medium transition-all ${
            isLoading || disabled
              ? 'bg-gray-600/50 text-gray-400 cursor-not-allowed'
              : 'bg-emerald-500/20 text-emerald-400 hover:bg-emerald-500/30 border border-emerald-500/50'
          }`}
        >
          {isLoading ? (
            <span className="flex items-center gap-2">
              <div className="w-4 h-4 border-2 border-emerald-400/30 border-t-emerald-400 rounded-full animate-spin" />
              Loading...
            </span>
          ) : (
            <span className="flex items-center gap-2">
              <svg className="w-4 h-4" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M9 12h6m-6 4h6m2 5H7a2 2 0 01-2-2V5a2 2 0 012-2h5.586a1 1 0 01.707.293l5.414 5.414a1 1 0 01.293.707V19a2 2 0 01-2 2z" />
              </svg>
              Get Captions
            </span>
          )}
        </button>
      </div>
    </motion.div>
  )
}
