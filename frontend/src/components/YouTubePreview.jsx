import { motion } from 'framer-motion'

export default function YouTubePreview({ videoData, analysisResults }) {
  if (!videoData || videoData.type !== 'youtube') return null

  const { videoId } = videoData
  const embedUrl = `https://www.youtube.com/embed/${videoId}`
  const thumbnailUrl = `https://img.youtube.com/vi/${videoId}/hqdefault.jpg`

  const quickCheck = analysisResults?.quick_check
  const videoInfo = analysisResults?.video_info

  const getVerdictColor = () => {
    if (!quickCheck) return 'bg-emerald-500'
    if (quickCheck.verdict === 'LIKELY SAFE') return 'bg-emerald-500'
    if (quickCheck.verdict === 'CAUTION') return 'bg-amber-500'
    return 'bg-red-500'
  }

  return (
    <motion.div
      initial={{ opacity: 0, y: 20 }}
      animate={{ opacity: 1, y: 0 }}
      className="card overflow-hidden mb-8"
    >
      {/* Video Preview */}
      <div className="aspect-video bg-black relative">
        <iframe
          src={embedUrl}
          title="YouTube Video Preview"
          className="w-full h-full"
          frameBorder="0"
          allow="accelerometer; autoplay; clipboard-write; encrypted-media; gyroscope; picture-in-picture"
          allowFullScreen
        />
        
        {/* Verdict Badge */}
        {quickCheck && (
          <div className={`absolute top-4 right-4 ${getVerdictColor()} text-white px-4 py-2 rounded-full font-bold text-sm shadow-lg`}>
            {quickCheck.verdict}
          </div>
        )}
      </div>

      {/* Video Info */}
      {videoInfo && (
        <div className="p-4 border-b border-white/10">
          <h3 className="font-bold text-lg line-clamp-2">{videoInfo.title}</h3>
          <p className="text-secondary text-sm mt-1">{videoInfo.channel}</p>
        </div>
      )}

      {/* Quick Analysis Result */}
      {analysisResults && (
        <div className="p-6">
          <div className="flex items-center justify-between mb-4">
            <div className="flex items-center gap-3">
              <div className={`w-4 h-4 rounded-full ${
                (analysisResults.score || 0) < 30 ? 'bg-emerald-500' :
                (analysisResults.score || 0) < 50 ? 'bg-amber-500' :
                'bg-red-500'
              }`} />
              <span className="font-semibold">Safety Score</span>
            </div>
            <div className="text-right">
              <div className="text-2xl font-bold">{analysisResults.score || 0}%</div>
              <div className="text-xs text-secondary">
                {analysisResults.verdict === 'safe' ? 'Safe' :
                 analysisResults.verdict === 'warning' ? 'Review Recommended' :
                 'High Risk'}
              </div>
            </div>
          </div>

          {/* Risk Bar */}
          <div className="h-2 bg-white/10 rounded-full overflow-hidden mb-4">
            <div
              className={`h-full transition-all duration-500 ${
                (analysisResults.score || 0) < 30 ? 'bg-emerald-500' :
                (analysisResults.score || 0) < 50 ? 'bg-amber-500' :
                'bg-red-500'
              }`}
              style={{ width: `${100 - (analysisResults.score || 0)}%` }}
            />
          </div>

          {/* Quick Recommendation */}
          <div className="p-4 rounded-lg bg-white/5">
            <p className="text-sm text-secondary">
              <span className="font-semibold text-white">Recommendation: </span>
              {quickCheck?.recommendation || 'Review content before posting'}
            </p>
          </div>
        </div>
      )}

      {/* Loading State */}
      {!analysisResults && (
        <div className="p-6 text-center">
          <div className="w-8 h-8 border-2 border-emerald-500/30 border-t-emerald-500 rounded-full animate-spin mx-auto mb-4" />
          <p className="text-secondary">Analyzing video content...</p>
        </div>
      )}
    </motion.div>
  )
}
