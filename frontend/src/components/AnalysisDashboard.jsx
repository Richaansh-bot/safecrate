import { motion } from 'framer-motion'

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
  const { categories, overall, verdict, score } = results
  
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

  const sortedCategories = Object.entries(categories)
    .sort((a, b) => b[1].score - a[1].score)

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
          <span className="text-2xl font-bold gradient-safe">{score}%</span>
        </div>
        <div className="progress-bar">
          <div
            className="progress-fill bg-gradient-to-r from-emerald-500 to-emerald-400"
            style={{ width: `${score}%` }}
          />
        </div>
      </div>

      {/* Category Breakdown */}
      <h3 className="text-xl font-bold mb-4">Analysis Details</h3>
      <div className="grid md:grid-cols-2 gap-4 mb-8">
        {sortedCategories.map(([key, data], index) => {
          const riskInfo = RISK_LABELS[data.risk_level] || RISK_LABELS.safe
          const icon = CATEGORY_ICONS[key] || '📋'
          
          return (
            <motion.div
              key={key}
              initial={{ opacity: 0, y: 20 }}
              animate={{ opacity: 1, y: 0 }}
              transition={{ delay: index * 0.05 }}
              className={`category-card category-${data.risk_level}`}
            >
              <div className="flex items-start justify-between mb-3">
                <div className="flex items-center gap-3">
                  <span className="text-2xl">{icon}</span>
                  <div>
                    <h4 className="font-semibold">{data.category}</h4>
                    <span className={`text-xs px-2 py-0.5 rounded ${riskInfo.class}`}>
                      {riskInfo.text}
                    </span>
                  </div>
                </div>
                <span className="text-lg font-bold">
                  {(data.score * 100).toFixed(0)}%
                </span>
              </div>
              
              <div className="progress-bar mb-3">
                <div
                  className={`progress-fill ${
                    data.risk_level === 'safe' ? 'bg-emerald-500' :
                    data.risk_level === 'low' ? 'bg-lime-500' :
                    data.risk_level === 'medium' ? 'bg-amber-500' :
                    data.risk_level === 'high' ? 'bg-orange-500' :
                    'bg-red-500'
                  }`}
                  style={{ width: `${data.score * 100}%` }}
                />
              </div>

              {data.findings && data.findings.length > 0 && (
                <div className="mt-3 pt-3 border-t border-white/10">
                  <p className="text-sm text-amber-400">
                    ⚠️ {data.findings[0]}
                  </p>
                </div>
              )}

              {data.recommendations && data.recommendations.length > 0 && (
                <div className="mt-2">
                  <p className="text-xs text-secondary">
                    💡 {data.recommendations[0]}
                  </p>
                </div>
              )}
            </motion.div>
          )
        })}
      </div>

      {/* Recommendations */}
      <div className="card p-6">
        <h3 className="text-lg font-bold mb-4">Recommendations</h3>
        <ul className="space-y-3">
          {sortedCategories
            .filter(([_, data]) => data.recommendations?.length > 0)
            .flatMap(([_, data]) => data.recommendations || [])
            .slice(0, 5)
            .map((rec, i) => (
              <li key={i} className="flex items-start gap-3">
                <span className="text-emerald-500 mt-1">✓</span>
                <span className="text-secondary">{rec}</span>
              </li>
            ))}
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
