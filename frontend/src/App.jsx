import { useState } from 'react'
import Header from './components/Header'
import HeroSection from './components/HeroSection'
import VideoInput from './components/VideoInput'
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

function App() {
  const [activeTab, setActiveTab] = useState('analyzer')
  const [videoData, setVideoData] = useState(null)
  const [isAnalyzing, setIsAnalyzing] = useState(false)
  const [analysisResults, setAnalysisResults] = useState(null)

  const handleAnalyze = async (data) => {
    setVideoData(data)
    setIsAnalyzing(true)
    
    // Simulate analysis delay
    await new Promise(resolve => setTimeout(resolve, 2000))
    
    // Calculate overall score
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

  return (
    <div className="min-h-screen">
      <Header activeTab={activeTab} setActiveTab={setActiveTab} />
      
      <main className="pt-24 pb-16 px-4">
        <div className="max-w-6xl mx-auto">
          {activeTab === 'analyzer' && (
            <>
              <HeroSection />
              <VideoInput onAnalyze={handleAnalyze} isAnalyzing={isAnalyzing} />
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
                <h4 className="font-semibold">Enter Video Details</h4>
                <p className="text-sm text-secondary">Title, description, and tags help us analyze content</p>
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
