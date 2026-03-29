import { useState } from 'react'

export default function VideoInput({ onAnalyze, isAnalyzing }) {
  const [title, setTitle] = useState('')
  const [description, setDescription] = useState('')
  const [tags, setTags] = useState('')

  const handleSubmit = (e) => {
    e.preventDefault()
    if (!title.trim()) return
    
    onAnalyze({
      title: title.trim(),
      description: description.trim(),
      tags: tags.split(',').map(t => t.trim()).filter(Boolean)
    })
  }

  return (
    <div className="max-w-2xl mx-auto animate-fadeIn">
      <form onSubmit={handleSubmit} className="card p-8">
        <h2 className="text-xl font-bold mb-6">Enter Video Details</h2>
        
        <div className="space-y-5">
          <div>
            <label className="block text-sm font-medium mb-2">
              Video Title <span className="text-red-400">*</span>
            </label>
            <input
              type="text"
              className="input"
              placeholder="e.g., My Morning Routine in Mumbai"
              value={title}
              onChange={(e) => setTitle(e.target.value)}
              required
            />
          </div>
          
          <div>
            <label className="block text-sm font-medium mb-2">
              Description
            </label>
            <textarea
              className="input min-h-[120px] resize-none"
              placeholder="Describe your video content..."
              value={description}
              onChange={(e) => setDescription(e.target.value)}
            />
          </div>
          
          <div>
            <label className="block text-sm font-medium mb-2">
              Tags (comma-separated)
            </label>
            <input
              type="text"
              className="input"
              placeholder="vlog, daily routine, lifestyle"
              value={tags}
              onChange={(e) => setTags(e.target.value)}
            />
          </div>
        </div>
        
        <button
          type="submit"
          className="btn-primary w-full mt-6 flex items-center justify-center gap-2"
          disabled={!title.trim() || isAnalyzing}
        >
          {isAnalyzing ? (
            <>
              <div className="w-5 h-5 border-2 border-white/30 border-t-white rounded-full animate-spin" />
              Analyzing...
            </>
          ) : (
            <>
              <svg className="w-5 h-5" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M9 12l2 2 4-4m5.618-4.016A11.955 11.955 0 0112 2.944a11.955 11.955 0 01-8.618 3.04A12.02 12.02 0 003 9c0 5.591 3.824 10.29 9 11.622 5.176-1.332 9-6.03 9-11.622 0-1.042-.133-2.052-.382-3.016z" />
              </svg>
              Analyze Content Safety
            </>
          )}
        </button>
      </form>

      <div className="mt-6 text-center text-sm text-secondary">
        <p>
          This tool provides safety guidance only. Always use your best judgment.
        </p>
      </div>
    </div>
  )
}
