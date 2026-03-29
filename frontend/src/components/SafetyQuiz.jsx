import { useState } from 'react'

const QUIZ_QUESTIONS = [
  {
    id: 'q1',
    question: 'Do all women appearing in the video know they are being filmed and have they given consent?',
    critical: true
  },
  {
    id: 'q2',
    question: 'Does your video portray women with dignity and respect?',
    critical: true
  },
  {
    id: 'q3',
    question: 'Is there any hidden camera or voyeuristic footage of women?',
    critical: true,
    reverse: true
  },
  {
    id: 'q4',
    question: 'Does your video use derogatory language toward women?',
    critical: true,
    reverse: true
  },
  {
    id: 'q5',
    question: 'Could someone use this video to harass or stalk women shown in it?',
    critical: true,
    reverse: true
  },
  {
    id: 'q6',
    question: 'Does the video show women in dangerous or unsafe situations?',
    critical: true,
    reverse: true
  },
  {
    id: 'q7',
    question: 'Is personal information (address, workplace) visible in the video?',
    critical: true,
    reverse: true
  },
  {
    id: 'q8',
    question: 'Does your content glorify or normalize violence against women?',
    critical: true,
    reverse: true
  },
  {
    id: 'q9',
    question: 'Is there body shaming of any kind in the video?',
    critical: true,
    reverse: true
  },
  {
    id: 'q10',
    question: 'Would you be comfortable if your sister/daughter/mother saw this video?',
    critical: false
  }
]

export default function SafetyQuiz() {
  const [answers, setAnswers] = useState({})
  const [showResult, setShowResult] = useState(false)

  const handleAnswer = (questionId, value, isReverse) => {
    setAnswers(prev => ({
      ...prev,
      [questionId]: { value, isReverse }
    }))
  }

  const calculateResult = () => {
    const answered = Object.keys(answers).length
    if (answered < 10) return null

    let passed = 0
    let criticalFails = 0

    QUIZ_QUESTIONS.forEach(q => {
      const answer = answers[q.id]
      if (!answer) return

      if (q.reverse) {
        // If reverse question and answer is NO (value=false), it's good
        if (!answer.value) {
          passed++
        } else if (q.critical) {
          criticalFails++
        }
      } else {
        // Normal question - YES is good
        if (answer.value) {
          passed++
        } else if (q.critical) {
          criticalFails++
        }
      }
    })

    const score = (passed / 10) * 100

    if (criticalFails >= 3 || score < 50) {
      return { verdict: 'danger', score, message: 'Your content has significant safety issues. We strongly recommend NOT posting without major revisions.' }
    } else if (criticalFails >= 1 || score < 70) {
      return { verdict: 'warning', score, message: 'Your content needs review before posting. Please address the critical issues identified.' }
    } else if (score < 85) {
      return { verdict: 'mostly_safe', score, message: 'Your content is mostly safe but could benefit from minor improvements.' }
    } else {
      return { verdict: 'safe', score, message: 'Your content appears safe from women\'s safety perspective. Always use your best judgment.' }
    }
  }

  const result = calculateResult()

  const getVerdictClass = () => {
    if (!result) return ''
    if (result.verdict === 'safe' || result.verdict === 'mostly_safe') return 'verdict-safe'
    if (result.verdict === 'warning') return 'verdict-warning'
    return 'verdict-danger'
  }

  return (
    <div className="py-8 animate-fadeIn">
      <div className="max-w-2xl mx-auto">
        <div className="text-center mb-8">
          <h1 className="text-3xl font-bold mb-3">
            Women's Safety <span className="gradient-safe">Quick Check</span>
          </h1>
          <p className="text-secondary">
            Answer these 10 questions to quickly assess if your content is safe for women
          </p>
        </div>

        <div className="space-y-4">
          {QUIZ_QUESTIONS.map((q, index) => (
            <div
              key={q.id}
              className={`card p-6 ${answers[q.id] ? 'border-emerald-500/30' : ''}`}
            >
              <div className="flex items-start gap-4">
                <div className="w-8 h-8 rounded-full bg-emerald-500/20 text-emerald-500 flex items-center justify-center font-bold flex-shrink-0">
                  {index + 1}
                </div>
                <div className="flex-1">
                  <p className="font-medium mb-4">
                    {q.question}
                    {q.critical && <span className="text-red-400 ml-1">*</span>}
                  </p>
                  <div className="flex gap-4">
                    <button
                      onClick={() => handleAnswer(q.id, true, q.reverse)}
                      className={`flex-1 py-3 rounded-lg font-medium transition-all ${
                        answers[q.id]?.value === true
                          ? 'bg-emerald-500/30 text-emerald-400 border-2 border-emerald-500'
                          : 'bg-white/5 hover:bg-white/10 border-2 border-transparent'
                      }`}
                    >
                      Yes
                    </button>
                    <button
                      onClick={() => handleAnswer(q.id, false, q.reverse)}
                      className={`flex-1 py-3 rounded-lg font-medium transition-all ${
                        answers[q.id]?.value === false
                          ? 'bg-red-500/30 text-red-400 border-2 border-red-500'
                          : 'bg-white/5 hover:bg-white/10 border-2 border-transparent'
                      }`}
                    >
                      No
                    </button>
                  </div>
                </div>
              </div>
            </div>
          ))}
        </div>

        {/* Result */}
        {result && (
          <div className={`card p-8 mt-8 text-center ${getVerdictClass()}`}>
            <div className="text-5xl mb-4">
              {result.verdict === 'safe' || result.verdict === 'mostly_safe' ? '✓' :
               result.verdict === 'warning' ? '⚠' : '✗'}
            </div>
            <h2 className="text-2xl font-bold mb-2">
              {result.verdict === 'safe' ? 'SAFE TO POST' :
               result.verdict === 'mostly_safe' ? 'MOSTLY SAFE' :
               result.verdict === 'warning' ? 'REVIEW NEEDED' : 'DO NOT POST'}
            </h2>
            <p className="text-secondary mb-4">{result.message}</p>
            <div className="text-3xl font-bold gradient-safe">
              {result.score.toFixed(0)}%
            </div>
          </div>
        )}

        {/* Progress */}
        <div className="mt-6 text-center text-secondary">
          <span>{Object.keys(answers).length} / 10 questions answered</span>
          <div className="progress-bar mt-2 max-w-xs mx-auto">
            <div
              className="progress-fill bg-emerald-500"
              style={{ width: `${(Object.keys(answers).length / 10) * 100}%` }}
            />
          </div>
        </div>
      </div>
    </div>
  )
}
