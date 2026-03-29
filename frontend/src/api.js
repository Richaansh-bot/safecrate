/**
 * Safecrate API Service
 * Handles all API calls to the backend
 */

const API_BASE = 'http://localhost:8001/api'

export async function analyzeYouTube(url, transcript = null) {
  try {
    const body = { url }
    if (transcript) {
      body.transcript = transcript
    }
    
    const response = await fetch(`${API_BASE}/analyze/youtube`, {
      method: 'POST',
      headers: {
        'Content-Type': 'application/json',
      },
      body: JSON.stringify(body),
    })
    
    if (!response.ok) {
      throw new Error('Analysis failed')
    }
    
    return await response.json()
  } catch (error) {
    console.error('YouTube analysis error:', error)
    throw error
  }
}

export async function analyzeText(title, description, tags) {
  try {
    const response = await fetch(`${API_BASE}/analyze/text`, {
      method: 'POST',
      headers: {
        'Content-Type': 'application/json',
      },
      body: JSON.stringify({ title, description, tags }),
    })
    
    if (!response.ok) {
      throw new Error('Analysis failed')
    }
    
    return await response.json()
  } catch (error) {
    console.error('Text analysis error:', error)
    throw error
  }
}

export async function quickCheck(url) {
  try {
    const response = await fetch(`${API_BASE}/quick-check?url=${encodeURIComponent(url)}`)
    return await response.json()
  } catch (error) {
    console.error('Quick check error:', error)
    return { valid: false }
  }
}

export async function healthCheck() {
  try {
    const response = await fetch(`${API_BASE}/health`)
    return await response.json()
  } catch (error) {
    return { status: 'offline' }
  }
}

// Extract video ID from various YouTube URL formats
export function extractVideoId(url) {
  const patterns = [
    /youtube\.com\/watch\?v=([a-zA-Z0-9_-]{11})/,
    /youtu\.be\/([a-zA-Z0-9_-]{11})/,
    /youtube\.com\/embed\/([a-zA-Z0-9_-]{11})/,
    /youtube\.com\/shorts\/([a-zA-Z0-9_-]{11})/,
    /youtube\.com\/live\/([a-zA-Z0-9_-]{11})/,
  ]
  
  for (const pattern of patterns) {
    const match = url.match(pattern)
    if (match) return match[1]
  }
  return null
}

// Validate YouTube URL
export function isValidYouTubeUrl(url) {
  const patterns = [
    /^(https?:\/\/)?(www\.)?youtube\.com\/watch\?v=/,
    /^(https?:\/\/)?(www\.)?youtu\.be\//,
    /^(https?:\/\/)?(www\.)?youtube\.com\/embed\//,
    /^(https?:\/\/)?(www\.)?youtube\.com\/shorts\//,
  ]
  return patterns.some(pattern => pattern.test(url))
}
