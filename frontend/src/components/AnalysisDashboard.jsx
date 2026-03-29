import { motion } from 'framer-motion'
import EvidenceTimeline from './EvidenceTimeline'

const CATEGORY_ICONS = {
  women_safety: '👩',
  violence: '⚔️',
  sexual_content: '🔞',
  harassment: '⚠️',
  privacy: '🔒',
  legal: '⚖️',
  cultural_sensitivity: '🕌',
  self_harm: '💔',
  dangerous_activities: '⚡',
  misinformation: '📢'
}

const RISK_LABELS = {
  safe: { text: 'Safe', class: 'risk-safe' },
  low: { text: 'Low Risk', class: 'risk-low' },
  medium: { text: 'Medium Risk', class: 'risk-medium' },
  high: { text: 'High Risk', class: 'risk-high' },
  critical: { text: 'Critical', class: 'risk-critical' }
}

export default function AnalysisDashboard({ videoData, results }) {
  const { categories, score, verdict } = results
  
  const sortedCategories = Object.entries(categories || {})
    .sort((a, b) => (b[1]?.score || 0) - (a[1]?.score || 0))

  const getVerdictClass = () => {
    if (verdict === 'safe') return 'verdict-safe'
    if (verdict === 'warning') return 'verdict-warning'
    return 'verdict-danger'
  }

  const getVerdictText = () => {
    if (verdict === 'safe') return 'Safe to Post'
    if (verdict === 'warning') return 'Review Recommended'
    return 'Do Not Post'
  }

  const getScoreColor = () => {
    if (score < 30) return 'text-emerald-500'
    if (score < 50) return 'text-amber-500'
    return 'text-red-500'
  }

  const getProgressColor = () => {
    if (score < 30) return 'bg-emerald-500'
    if (score < 50) return 'bg-amber-500'
    return 'bg-red-500'
  }

  return (
    <motion.div
      initial={{ opacity: 0, y: 30 }}
      animate={{ opacity: 1, y: 0 }}
      transition={{ duration: 0.5 }}
      className="mt-12"
    >
      {/* Verdict Banner */}
      <div className={`verdict-badge ${getVerdictClass()} mx-auto mb-8`}>
        <span className="text-2xl">
          {verdict === 'safe' ? '✓' : verdict === 'warning' ? '⚠' : '✗'}
        </span>
        <span>{getVerdictText()}</span>
        <span className="text-lg opacity-70">({score}%)</span>
      </div>

      {/* Score Bar */}
      <div className="card p-6 mb-8">
        <div className="flex items-center justify-between mb-3">
          <span className="font-semibold">Overall Safety Score</span>
          <span className={`text-2xl font-bold ${getScoreColor()}`}>{score}%</span>
        </div>
        <div className="progress-bar">
          <div
            className={`progress-fill ${getProgressColor()}`}
            style={{ width: `${100 - score}%` }}
          />
        </div>
        <p className="text-sm text-secondary mt-3">
          Lower is safer. Content with scores above 50% may need review.
        </p>
      </div>

      {/* Category Breakdown */}
      {sortedCategories.length > 0 && (
        <>
          <h3 className="text-xl font-bold mb-4">Analysis Details</h3>
          <div className="grid md:grid-cols-2 gap-4 mb-8">
            {sortedCategories.map(([key, data], index) => {
              if (!data) return null
              
              const riskInfo = RISK_LABELS[data.risk_level] || RISK_LABELS.safe
              const icon = CATEGORY_ICONS[key] || '📋'
              const displayScore = Math.round((data.score || 0) * 100)
              
              return (
                <motion.div
                  key={key}
                  initial={{ opacity: 0, y: 20 }}
                  animate={{ opacity: 1, y: 0 }}
                  transition={{ delay: index * 0.05 }}
                  className={`category-card category-${data.risk_level || 'safe'}`}
                >
                  <div className="flex items-start justify-between mb-3">
                    <div className="flex items-center gap-3">
                      <span className="text-2xl">{icon}</span>
                      <div>
                        <h4 className="font-semibold">{data.category || key.replace('_', ' ')}</h4>
                        <span className={`text-xs px-2 py-0.5 rounded ${riskInfo.class}`}>
                          {riskInfo.text}
                        </span>
                      </div>
                    </div>
                    <span className={`text-lg font-bold ${
                      displayScore < 30 ? 'text-emerald-500' :
                      displayScore < 50 ? 'text-amber-500' :
                      'text-red-500'
                    }`}>
                      {displayScore}%
                    </span>
                  </div>
                  
                  <div className="progress-bar mb-3">
                    <div
                      className={`progress-fill ${
                        displayScore < 30 ? 'bg-emerald-500' :
                        displayScore < 50 ? 'bg-amber-500' :
                        'bg-red-500'
                      }`}
                      style={{ width: `${displayScore}%` }}
                    />
                  </div>

                  {(data.findings?.length > 0 || data.recommendations?.length > 0) && (
                    <div className="mt-3 pt-3 border-t border-white/10 space-y-2">
                      {data.findings?.map((finding, i) => (
                        <p key={i} className="text-sm text-amber-400 flex items-start gap-2">
                          <span>⚠️</span>
                          <span>{finding}</span>
                        </p>
                      ))}
                      {data.recommendations?.slice(0, 2).map((rec, i) => (
                        <p key={i} className="text-xs text-secondary flex items-start gap-2">
                          <span>💡</span>
                          <span>{rec}</span>
                        </p>
                      ))}
                    </div>
                  )}

                  {/* Evidence Timeline */}
                  {data.evidence && data.evidence.length > 0 && (
                    <EvidenceTimeline evidence={data.evidence} />
                  )}
                </motion.div>
              )
            })}
          </div>
        </>
      )}

      {/* Recommendations Summary */}
      <div className="card p-6">
        <h3 className="text-lg font-bold mb-4">Recommendations</h3>
        <ul className="space-y-3">
          {sortedCategories
            .filter(([_, data]) => data?.recommendations?.length > 0)
            .flatMap(([_, data]) => data.recommendations || [])
            .filter(Boolean)
            .slice(0, 5)
            .map((rec, i) => (
              <li key={i} className="flex items-start gap-3">
                <span className="text-emerald-500 mt-0.5">✓</span>
                <span className="text-secondary">{rec}</span>
              </li>
            ))}
          {sortedCategories.filter(([_, data]) => data?.findings?.length > 0).length === 0 && (
            <li className="flex items-start gap-3">
              <span className="text-emerald-500 mt-0.5">✓</span>
              <span className="text-secondary">No critical issues found. Content appears safe to post.</span>
            </li>
          )}
        </ul>
      </div>

      {/* Disclaimer */}
      <div className="mt-8 p-4 rounded-lg bg-white/5 text-center">
        <p className="text-xs text-secondary">
          ⚠️ This analysis is for guidance only and does not constitute legal advice.
          Always use your best judgment and consult professionals when needed.
        </p>
      </div>
    </motion.div>
  )
}
