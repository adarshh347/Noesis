'use client'

import { PragmaticFlow as PragmaticFlowType } from '@/types'
import { ArrowRight, Lightbulb, Target } from 'lucide-react'

interface PragmaticFlowProps {
  flow: PragmaticFlowType
}

export default function PragmaticFlow({ flow }: PragmaticFlowProps) {
  return (
    <div className="space-y-6">
      {/* Themes */}
      <div>
        <h4 className="text-lg font-semibold mb-3 flex items-center gap-2">
          <Target className="w-5 h-5 text-philosophy-glow" />
          Core Themes
        </h4>
        <div className="flex flex-wrap gap-2">
          {flow.themes.map((theme, idx) => (
            <span
              key={idx}
              className="px-4 py-2 bg-philosophy-glow/20 border border-philosophy-glow rounded-lg"
            >
              {theme}
            </span>
          ))}
        </div>
      </div>

      {/* Applications */}
      <div>
        <h4 className="text-lg font-semibold mb-3 flex items-center gap-2">
          <Lightbulb className="w-5 h-5 text-philosophy-light" />
          Pragmatic Applications
        </h4>
        <div className="grid grid-cols-1 md:grid-cols-2 gap-3">
          {flow.applications.map((app, idx) => (
            <div
              key={idx}
              className="p-4 bg-philosophy-dark/50 border border-philosophy-light rounded-lg card-hover"
            >
              <p className="text-gray-300">{app}</p>
            </div>
          ))}
        </div>
      </div>

      {/* Connections */}
      {flow.connections && flow.connections.length > 0 && (
        <div>
          <h4 className="text-lg font-semibold mb-3 flex items-center gap-2">
            <ArrowRight className="w-5 h-5 text-philosophy-accent" />
            Theme → Application Connections
          </h4>
          <div className="space-y-2">
            {flow.connections.slice(0, 10).map((conn, idx) => (
              <div
                key={idx}
                className="flex items-center gap-3 p-3 bg-philosophy-dark/30 rounded-lg"
              >
                <span className="text-philosophy-glow font-medium">{conn.from}</span>
                <ArrowRight className="w-4 h-4 text-gray-500" />
                <span className="text-gray-300">{conn.to}</span>
              </div>
            ))}
          </div>
        </div>
      )}
    </div>
  )
}

