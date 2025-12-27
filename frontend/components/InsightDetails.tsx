'use client'

import { Insights } from '@/types'
import { Brain, Link2, Zap, Eye } from 'lucide-react'

interface InsightDetailsProps {
  insights: Insights
}

export default function InsightDetails({ insights }: InsightDetailsProps) {
  return (
    <div className="philosophy-gradient rounded-2xl p-6">
      <h3 className="text-2xl font-bold mb-6 flex items-center gap-2">
        <Brain className="w-6 h-6" />
        Extracted Insights
      </h3>

      <div className="grid grid-cols-1 md:grid-cols-2 gap-6">
        {/* Themes */}
        {insights.themes && insights.themes.length > 0 && (
          <div>
            <h4 className="text-lg font-semibold mb-3 flex items-center gap-2">
              <Eye className="w-5 h-5 text-philosophy-glow" />
              Core Themes
            </h4>
            <ul className="space-y-2">
              {insights.themes.map((theme, idx) => (
                <li key={idx} className="p-3 bg-philosophy-dark/50 rounded-lg border border-philosophy-light">
                  {theme}
                </li>
              ))}
            </ul>
          </div>
        )}

        {/* Concepts */}
        {insights.concepts && insights.concepts.length > 0 && (
          <div>
            <h4 className="text-lg font-semibold mb-3 flex items-center gap-2">
              <Brain className="w-5 h-5 text-philosophy-light" />
              Key Concepts
            </h4>
            <div className="flex flex-wrap gap-2">
              {insights.concepts.map((concept, idx) => (
                <span
                  key={idx}
                  className="px-3 py-1 bg-philosophy-accent/50 rounded-full text-sm"
                >
                  {concept}
                </span>
              ))}
            </div>
          </div>
        )}

        {/* Connections */}
        {insights.connections && insights.connections.length > 0 && (
          <div>
            <h4 className="text-lg font-semibold mb-3 flex items-center gap-2">
              <Link2 className="w-5 h-5 text-philosophy-accent" />
              Philosophical Connections
            </h4>
            <div className="flex flex-wrap gap-2">
              {insights.connections.map((conn, idx) => (
                <span
                  key={idx}
                  className="px-3 py-1 bg-philosophy-light/30 rounded-full text-sm border border-philosophy-light"
                >
                  {conn}
                </span>
              ))}
            </div>
          </div>
        )}

        {/* Pragmatic Applications */}
        {insights.pragmatic_applications && insights.pragmatic_applications.length > 0 && (
          <div>
            <h4 className="text-lg font-semibold mb-3 flex items-center gap-2">
              <Zap className="w-5 h-5 text-philosophy-glow" />
              Pragmatic Applications
            </h4>
            <ul className="space-y-2">
              {insights.pragmatic_applications.map((app, idx) => (
                <li key={idx} className="p-3 bg-philosophy-dark/50 rounded-lg border-l-4 border-philosophy-glow">
                  {app}
                </li>
              ))}
            </ul>
          </div>
        )}
      </div>

      {/* Visual Metaphors */}
      {insights.visual_metaphors && insights.visual_metaphors.length > 0 && (
        <div className="mt-6">
          <h4 className="text-lg font-semibold mb-3">Visual Metaphors</h4>
          <div className="flex flex-wrap gap-2">
            {insights.visual_metaphors.map((metaphor, idx) => (
              <span
                key={idx}
                className="px-4 py-2 bg-philosophy-glow/10 border border-philosophy-glow rounded-lg italic"
              >
                {metaphor}
              </span>
            ))}
          </div>
        </div>
      )}
    </div>
  )
}

