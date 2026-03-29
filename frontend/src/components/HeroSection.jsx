import { motion } from 'framer-motion'

export default function HeroSection() {
  return (
    <section className="text-center py-16 animate-fadeIn">
      <motion.div
        initial={{ opacity: 0, y: 20 }}
        animate={{ opacity: 1, y: 0 }}
        transition={{ delay: 0.1 }}
        className="mb-6"
      >
        <span className="inline-flex items-center gap-2 px-4 py-2 rounded-full bg-emerald-500/10 text-emerald-400 text-sm font-medium">
          <span className="w-2 h-2 rounded-full bg-emerald-500 animate-pulse" />
          Made for Indian Content Creators
        </span>
      </motion.div>

      <motion.h1
        initial={{ opacity: 0, y: 20 }}
        animate={{ opacity: 1, y: 0 }}
        transition={{ delay: 0.2 }}
        className="text-4xl md:text-5xl font-bold mb-6"
      >
        Is Your Content <span className="gradient-safe">Safe to Post</span>?
      </motion.h1>

      <motion.p
        initial={{ opacity: 0, y: 20 }}
        animate={{ opacity: 1, y: 0 }}
        transition={{ delay: 0.3 }}
        className="text-lg text-secondary max-w-2xl mx-auto mb-8"
      >
        Get instant safety analysis for your videos. Check women's safety, 
        legal compliance, and cultural sensitivity before you post.
      </motion.p>

      <motion.div
        initial={{ opacity: 0, y: 20 }}
        animate={{ opacity: 1, y: 0 }}
        transition={{ delay: 0.4 }}
        className="flex flex-wrap justify-center gap-6 text-sm"
      >
        <div className="flex items-center gap-2 text-secondary">
          <span className="text-emerald-500">✓</span>
          Women's Safety Check
        </div>
        <div className="flex items-center gap-2 text-secondary">
          <span className="text-emerald-500">✓</span>
          IT Act Compliance
        </div>
        <div className="flex items-center gap-2 text-secondary">
          <span className="text-emerald-500">✓</span>
          Privacy Protection
        </div>
        <div className="flex items-center gap-2 text-secondary">
          <span className="text-emerald-500">✓</span>
          Cultural Sensitivity
        </div>
      </motion.div>
    </section>
  )
}
