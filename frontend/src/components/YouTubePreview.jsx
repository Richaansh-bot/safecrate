import { motion } from 'framer-motion'

export default function YouTubePreview({ videoData, analysisResults }) {
  if (!videoData || videoData.type !== 'youtube') return null

  const { videoId, embedUrl } = videoData

  return (
    <motion.div
      initial={{ opacity: 0, y: 20 }}
      animate={{ opacity: 1, y: 0 }}
      className="card overflow-hidden mb-8"
    >
      {/* Video Preview */}
      <div className="aspect-video bg-black">
        <iframe
          src={embedUrl}
          title="YouTube Video Preview"
          className="w-full h-full"
          frameBorder="0"
          allow="accelerometer; autoplay; clipboard-write; encrypted-media; gyroscope; picture-in-picture"
          allowFullScreen
        />
      </div>

      {/* Quick Analysis Result */}
      {analysisResults && (
        <div className="p-6">
          <div className="flex items-center justify-between mb-4">
            <div className="flex items-center gap-3">
              <div className={`w-4 h-4 rounded-full ${
                analysisResults.quick_check?.verdict === 'LIKELY SAFE' ? 'bg-emerald-500' :
                analysisResults.quick_check?.verdict === 'CAUTION' ? 'bg-amber-500' :
                'bg-red-500'
              }`} />
              <span className="font-semibold">
                {analysisResults.quick_check?.verdict || 'ANALYZING'}
              </span>
            </div>
            <div className="text-right">
              <div className="text-2xl font-bold">
                {Math.round((analysisResults.quick_check?.risk_score || 0) * 100)}%
              </div>
              <div className="text-xs text-secondary">Risk Score</div>
            </div>
          </div>

          {/* Risk Bar */}
          <div className="h-2 bg-white/10 rounded-full overflow-hidden mb-4">
            <div
              className={`h-full transition-all duration-500 ${
                (analysisResults.quick_check?.risk_score || 0) < 0.3 ? 'bg-emerald-500' :
                (analysisResults.quick_check?.risk_score || 0) < 0.5 ? 'bg-amber-500' :
                'bg-red-500'
              }`}
              style={{ width: `${(analysisResults.quick_check?.risk_score || 0) * 100}%` }}
            />
          </div>

          {/* Detected Keywords */}
          {analysisResults.quick_check?.detected_keywords?.length > 0 && (
            <div className="flex flex-wrap gap-2">
              {analysisResults.quick_check.detected_keywords.map((keyword, i) => (
                <span
                  key={i}
                  className="px-3 py-1 bg-amber-500/20 text-amber-400 rounded-full text-sm"
                >
                  {keyword}
                </span>
              ))}
            </div>
          )}

          {/* Recommendation */}
          <p className="mt-4 text-sm text-secondary">
            {analysisResults.quick_check?.recommendation}
          </p>
        </div>
      )}
    </motion.div>
  )
}
