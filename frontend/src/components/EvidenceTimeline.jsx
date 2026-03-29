import { motion } from 'framer-motion'
import { useState } from 'react'

const severityColors = {
  low: 'text-amber-400',
  medium: 'text-orange-400',
  high: 'text-red-400',
  critical: 'text-red-600'
}

const severityBg = {
  low: 'bg-amber-500/20 border-amber-500/30',
  medium: 'bg-orange-500/20 border-orange-500/30',
  high: 'bg-red-500/20 border-red-500/30',
  critical: 'bg-red-600/30 border-red-600/40'
}

const locationIcons = {
  title: '📝',
  description: '📄',
  tags: '🏷️',
  transcript: '🎤'
}

const locationLabels = {
  title: 'Video Title',
  description: 'Description',
  tags: 'Tags',
  transcript: 'Video Transcript'
}

export default function EvidenceTimeline({ evidence = [] }) {
  const [expandedIndex, setExpandedIndex] = useState(null)

  if (!evidence || evidence.length === 0) {
    return null
  }

  // Sort by severity (critical first) then by weight
  const sortedEvidence = [...evidence].sort((a, b) => {
    const severityOrder = { critical: 0, high: 1, medium: 2, low: 3 }
    const severityDiff = (severityOrder[a.severity] || 2) - (severityOrder[b.severity] || 2)
    if (severityDiff !== 0) return severityDiff
    return (b.weight || 0) - (a.weight || 0)
  })

  return (
    <div className="mt-4">
      <div className="flex items-center gap-2 mb-3">
        <div className="w-2 h-2 rounded-full bg-emerald-500 animate-pulse" />
        <span className="text-sm font-medium text-emerald-400">
          Evidence Timeline ({sortedEvidence.length} items)
        </span>
      </div>

      <div className="relative pl-4 space-y-3">
        {/* Timeline line */}
        <div className="absolute left-[7px] top-2 bottom-2 w-[2px] bg-gradient-to-b from-emerald-500 via-emerald-500/50 to-transparent" />

        {sortedEvidence.map((item, index) => {
          const isExpanded = expandedIndex === index
          const severity = item.severity || 'medium'
          const colorClass = severityColors[severity] || severityColors.medium
          const bgClass = severityBg[severity] || severityBg.medium
          const locationIcon = locationIcons[item.location] || '📍'
          const locationLabel = locationLabels[item.location] || item.location

          return (
            <motion.div
              key={`${item.keyword}-${index}`}
              initial={{ opacity: 0, x: -20 }}
              animate={{ opacity: 1, x: 0 }}
              transition={{ delay: index * 0.05 }}
              className="relative"
            >
              {/* Timeline dot */}
              <div className={`absolute -left-[21px] top-3 w-3 h-3 rounded-full border-2 ${bgClass.replace('bg-', 'bg-opacity-20 border-').replace('/20', '')} ${bgClass.replace('/20', '/40').replace('bg-', 'bg-').replace('/30', '/50').replace('/40', '/60')} shadow-lg`}
                   style={{
                     backgroundColor: severity === 'critical' ? '#dc2626' : 
                                      severity === 'high' ? '#ef4444' : 
                                      severity === 'medium' ? '#f97316' : '#f59e0b',
                     boxShadow: `0 0 10px ${severity === 'critical' ? '#dc2626' : 
                                               severity === 'high' ? '#ef4444' : 
                                               severity === 'medium' ? '#f97316' : '#f59e0b'}40`
                   }}
              />

              {/* Evidence card */}
              <div 
                className={`p-3 rounded-lg border ${bgClass} cursor-pointer transition-all hover:scale-[1.01]`}
                onClick={() => setExpandedIndex(isExpanded ? null : index)}
              >
                {/* Header */}
                <div className="flex items-start justify-between gap-3">
                  <div className="flex-1 min-w-0">
                    <div className="flex items-center gap-2 mb-1">
                      <span className="text-lg">{locationIcon}</span>
                      <span className={`text-sm font-semibold ${colorClass}`}>
                        Found "{item.keyword}"
                      </span>
                      <span className={`text-xs px-2 py-0.5 rounded-full ${bgClass}`}>
                        +{item.weight?.toFixed(0)}%
                      </span>
                    </div>
                    <div className="flex items-center gap-2 text-xs text-gray-400">
                      <span>{locationLabel}</span>
                      <span>•</span>
                      <span className={`uppercase font-medium ${colorClass}`}>{severity}</span>
                    </div>
                  </div>
                  
                  <svg 
                    className={`w-4 h-4 text-gray-400 transition-transform ${isExpanded ? 'rotate-180' : ''}`}
                    fill="none" 
                    stroke="currentColor" 
                    viewBox="0 0 24 24"
                  >
                    <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M19 9l-7 7-7-7" />
                  </svg>
                </div>

                {/* Expanded content */}
                {isExpanded && (
                  <motion.div
                    initial={{ opacity: 0, height: 0 }}
                    animate={{ opacity: 1, height: 'auto' }}
                    className="mt-3 pt-3 border-t border-white/10"
                  >
                    <p className="text-xs text-gray-400 mb-2">Context:</p>
                    <p className="text-sm text-gray-200 bg-black/20 p-2 rounded font-mono leading-relaxed">
                      {item.context}
                    </p>
                  </motion.div>
                )}
              </div>
            </motion.div>
          )
        })}
      </div>
    </div>
  )
}
