import { useState } from 'react'
import Header from './components/Header'
import HeroSection from './components/HeroSection'
import VideoInput from './components/VideoInput'
import YouTubeInput from './components/YouTubeInput'
import YouTubePreview from './components/YouTubePreview'
import AnalysisDashboard from './components/AnalysisDashboard'
import SafetyQuiz from './components/SafetyQuiz'
import Footer from './components/Footer'

// Sample analysis data (simulating backend analysis)
const SAMPLE_ANALYSIS = {
  women_safety: {
    category: 'Women Safety',
    score: 0.65,
    risk_level: 'medium',
    findings: ['Content may affect viewer comfort', 'Review portrayal of subjects'],
    recommendations: ['Add content warning', 'Review for consent']
  },
  violence: {
    category: 'Violence',
    score: 0.2,
    risk_level: 'low',
    findings: [],
    recommendations: []
  },
  sexual_content: {
    category: 'Sexual Content',
    score: 0.1,
    risk_level: 'safe',
    findings: [],
    recommendations: []
  },
  harassment: {
    category: 'Harassment',
    score: 0.3,
    risk_level: 'low',
    findings: [],
    recommendations: []
  },
  privacy: {
    category: 'Privacy',
    score: 0.5,
    risk_level: 'medium',
    findings: ['Personal locations may be visible'],
    recommendations: ['Blur identifying information']
  },
  legal: {
    category: 'Legal Compliance',
    score: 0.7,
    risk_level: 'low',
    findings: [],
    recommendations: ['Review IT Act compliance']
  },
  cultural_sensitivity: {
    category: 'Cultural Sensitivity',
    score: 0.15,
    risk_level: 'safe',
    findings: [],
    recommendations: []
  },
  self_harm: {
    category: 'Self-Harm',
    score: 0.0,
    risk_level: 'safe',
    findings: [],
    recommendations: []
  },
  dangerous_activities: {
    category: 'Dangerous Activities',
    score: 0.1,
    risk_level: 'safe',
    findings: [],
    recommendations: []
  },
  misinformation: {
    category: 'Misinformation',
    score: 0.25,
    risk_level: 'low',
    findings: [],
    recommendations: []
  }
}

// Quick analysis based on content type
const QUICK_ANALYSIS = {
  youtube_video: {
    women_safety: { score: 0.55, risk_level: 'medium', findings: ['Analyze video content'] },
    violence: { score: 0.3, risk_level: 'low', findings: [] },
    sexual_content: { score: 0.15, risk_level: 'safe', findings: [] },
    harassment: { score: 0.25, risk_level: 'low', findings: [] },
    privacy: { score: 0.4, risk_level: 'low', findings: ['Check for personal info'] },
    legal: { score: 0.6, risk_level: 'low', findings: [] },
    cultural_sensitivity: { score: 0.2, risk_level: 'safe', findings: [] },
    self_harm: { score: 0.0, risk_level: 'safe', findings: [] },
    dangerous_activities: { score: 0.15, risk_level: 'safe', findings: [] },
    misinformation: { score: 0.1, risk_level: 'safe', findings: [] }
  }
}

function App() {
  const [activeTab, setActiveTab] = useState('analyzer')
  const [inputMode, setInputMode] = useState('text') // 'text' or 'youtube'
  const [videoData, setVideoData] = useState(null)
  const [isAnalyzing, setIsAnalyzing] = useState(false)
  const [analysisResults, setAnalysisResults] = useState(null)

  const handleTextAnalyze = async (data) => {
    setVideoData({ type: 'text', ...data })
    setIsAnalyzing(true)
    
    await new Promise(resolve => setTimeout(resolve, 2000))
    
    const scores = Object.values(SAMPLE_ANALYSIS).map(s => s.score)
    const overall = scores.reduce((a, b) => a + b, 0) / scores.length
    
    setAnalysisResults({
      categories: SAMPLE_ANALYSIS,
      overall: overall,
      verdict: overall < 0.3 ? 'safe' : overall < 0.5 ? 'warning' : 'danger',
      score: (overall * 100).toFixed(0)
    })
    
    setIsAnalyzing(false)
  }

  const handleYouTubeAnalyze = async (data) => {
    setVideoData(data)
    setIsAnalyzing(true)
    
    // Simulate API call to backend
    await new Promise(resolve => setTimeout(resolve, 3000))
    
    // Analyze based on quick check
    const analysis = QUICK_ANALYSIS.youtube_video
    
    // Add category names
    const categoryNames = {
      women_safety: 'Women Safety',
      violence: 'Violence',
      sexual_content: 'Sexual Content',
      harassment: 'Harassment',
      privacy: 'Privacy',
      legal: 'Legal Compliance',
      cultural_sensitivity: 'Cultural Sensitivity',
      self_harm: 'Self-Harm',
      dangerous_activities: 'Dangerous Activities',
      misinformation: 'Misinformation'
    }
    
    const categories = {}
    for (const [key, value] of Object.entries(analysis)) {
      categories[key] = {
        category: categoryNames[key],
        ...value
      }
    }
    
    // Calculate overall
    const scores = Object.values(categories).map(s => s.score)
    const overall = scores.reduce((a, b) => a + b, 0) / scores.length
    
    setAnalysisResults({
      categories,
      overall,
      verdict: overall < 0.3 ? 'safe' : overall < 0.5 ? 'warning' : 'danger',
      score: (overall * 100).toFixed(0),
      quick_check: {
        risk_score: overall,
        verdict: overall < 0.3 ? 'LIKELY SAFE' : overall < 0.5 ? 'CAUTION' : 'REVIEW NEEDED',
        color: overall < 0.3 ? '#22c55e' : overall < 0.5 ? '#eab308' : '#f97316',
        detected_keywords: ['video content'],
        recommendation: overall < 0.3 
          ? 'Content appears safe. Full analysis recommended.'
          : overall < 0.5
          ? 'Some risk factors detected. Review content.'
          : 'Multiple risk factors. Manual review recommended.'
      }
    })
    
    setIsAnalyzing(false)
  }

  return (
    <div className="min-h-screen">
      <Header activeTab={activeTab} setActiveTab={setActiveTab} />
      
      <main className="pt-24 pb-16 px-4">
        <div className="max-w-6xl mx-auto">
          {activeTab === 'analyzer' && (
            <>
              <HeroSection />
              
              {/* Input Mode Toggle */}
              <div className="flex justify-center mb-8">
                <div className="inline-flex bg-white/10 rounded-xl p-1">
                  <button
                    onClick={() => { setInputMode('youtube'); setAnalysisResults(null); }}
                    className={`px-6 py-3 rounded-lg font-medium transition-all ${
                      inputMode === 'youtube'
                        ? 'bg-red-500/20 text-red-400'
                        : 'text-secondary hover:text-white'
                    }`}
                  >
                    <span className="flex items-center gap-2">
                      <svg className="w-5 h-5" fill="currentColor" viewBox="0 0 24 24">
                        <path d="M19.615 3.184c-3.604-.246-11.631-.245-15.23 0C.488 3.45.029 5.804 0 12c.029 6.185.484 8.549 4.385 8.816 3.6.245 11.626.246 15.23 0C23.512 20.55 23.971 18.196 24 12c-.029-6.185-.484-8.549-4.385-8.816zM9 16V8l8 3.993L9 16z"/>
                      </svg>
                      YouTube Link
                    </span>
                  </button>
                  <button
                    onClick={() => { setInputMode('text'); setAnalysisResults(null); }}
                    className={`px-6 py-3 rounded-lg font-medium transition-all ${
                      inputMode === 'text'
                        ? 'bg-emerald-500/20 text-emerald-400'
                        : 'text-secondary hover:text-white'
                    }`}
                  >
                    <span className="flex items-center gap-2">
                      <svg className="w-5 h-5" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                        <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M11 5H6a2 2 0 00-2 2v11a2 2 0 002 2h11a2 2 0 002-2v-5m-1.414-9.414a2 2 0 112.828 2.828L11.828 15H9v-2.828l8.586-8.586z" />
                      </svg>
                      Text Input
                    </span>
                  </button>
                </div>
              </div>
              
              {/* YouTube Mode */}
              {inputMode === 'youtube' && (
                <>
                  <YouTubeInput 
                    onAnalyze={handleYouTubeAnalyze} 
                    isAnalyzing={isAnalyzing} 
                  />
                  {(videoData?.type === 'youtube' || analysisResults) && (
                    <YouTubePreview 
                      videoData={videoData} 
                      analysisResults={analysisResults} 
                    />
                  )}
                </>
              )}
              
              {/* Text Mode */}
              {inputMode === 'text' && (
                <VideoInput 
                  onAnalyze={handleTextAnalyze} 
                  isAnalyzing={isAnalyzing} 
                />
              )}
              
              {/* Analysis Results */}
              {analysisResults && (
                <AnalysisDashboard 
                  videoData={videoData} 
                  results={analysisResults} 
                />
              )}
            </>
          )}
          
          {activeTab === 'quiz' && (
            <SafetyQuiz />
          )}
          
          {activeTab === 'about' && (
            <AboutSection />
          )}
        </div>
      </main>
      
      <Footer />
    </div>
  )
}

function AboutSection() {
  return (
    <div className="py-16 animate-fadeIn">
      <div className="max-w-4xl mx-auto">
        <h1 className="text-4xl font-bold mb-8 text-center">
          About <span className="gradient-safe">Safecrate</span>
        </h1>
        
        <div className="card p-8 mb-8">
          <h2 className="text-2xl font-bold mb-4">Our Mission</h2>
          <p className="text-secondary leading-relaxed">
            Safecrate helps Indian content creators ensure their videos are safe, respectful, 
            and legally compliant before posting. We focus especially on protecting women's 
            safety and dignity in digital content.
          </p>
        </div>
        
        <div className="grid md:grid-cols-3 gap-6 mb-8">
          <div className="card p-6 text-center">
            <div className="text-4xl mb-4">🛡️</div>
            <h3 className="font-bold mb-2">Safety First</h3>
            <p className="text-sm text-secondary">
              Comprehensive checks for violence, harassment, and privacy concerns
            </p>
          </div>
          <div className="card p-6 text-center">
            <div className="text-4xl mb-4">⚖️</div>
            <h3 className="font-bold mb-2">Legal Compliance</h3>
            <p className="text-sm text-secondary">
              IT Act and IPC checks specific to Indian digital content laws
            </p>
          </div>
          <div className="card p-6 text-center">
            <div className="text-4xl mb-4">💪</div>
            <h3 className="font-bold mb-2">Women's Safety</h3>
            <p className="text-sm text-secondary">
              Special focus on ensuring content is safe for women viewers
            </p>
          </div>
        </div>
        
        <div className="card p-8">
          <h2 className="text-2xl font-bold mb-4">How It Works</h2>
          <div className="space-y-4">
            <div className="flex gap-4">
              <div className="w-8 h-8 rounded-full bg-emerald-500/20 text-emerald-500 flex items-center justify-center font-bold">1</div>
              <div>
                <h4 className="font-semibold">Enter Video or YouTube Link</h4>
                <p className="text-sm text-secondary">Paste a YouTube URL or enter video details</p>
              </div>
            </div>
            <div className="flex gap-4">
              <div className="w-8 h-8 rounded-full bg-emerald-500/20 text-emerald-500 flex items-center justify-center font-bold">2</div>
              <div>
                <h4 className="font-semibold">AI Analysis</h4>
                <p className="text-sm text-secondary">Our system checks for safety concerns across 10 categories</p>
              </div>
            </div>
            <div className="flex gap-4">
              <div className="w-8 h-8 rounded-full bg-emerald-500/20 text-emerald-500 flex items-center justify-center font-bold">3</div>
              <div>
                <h4 className="font-semibold">Get Recommendations</h4>
                <p className="text-sm text-secondary">Actionable suggestions to make your content safer</p>
              </div>
            </div>
          </div>
        </div>
      </div>
    </div>
  )
}

export default App
