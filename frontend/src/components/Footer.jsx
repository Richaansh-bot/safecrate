export default function Footer() {
  return (
    <footer className="py-8 px-4 border-t border-white/10">
      <div className="max-w-6xl mx-auto">
        <div className="flex flex-col md:flex-row items-center justify-between gap-4">
          <div className="flex items-center gap-3">
            <div className="w-8 h-8">
              <svg viewBox="0 0 100 100" className="w-full h-full">
                <defs>
                  <linearGradient id="footerGrad" x1="0%" y1="0%" x2="100%" y2="100%">
                    <stop offset="0%" stopColor="#10b981"/>
                    <stop offset="100%" stopColor="#059669"/>
                  </linearGradient>
                </defs>
                <path d="M50 5 L90 20 L90 45 C90 70 70 90 50 95 C30 90 10 70 10 45 L10 20 Z" fill="url(#footerGrad)"/>
              </svg>
            </div>
            <div>
              <div className="font-bold">Safecrate</div>
              <div className="text-xs text-secondary">Content Safety Validator</div>
            </div>
          </div>

          <div className="text-sm text-secondary">
            Made with ❤️ for safe content in India
          </div>

          <div className="text-xs text-secondary">
            ⚠️ For guidance only, not legal advice
          </div>
        </div>
      </div>
    </footer>
  )
}
