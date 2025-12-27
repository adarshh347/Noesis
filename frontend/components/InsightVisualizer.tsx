'use client'

import { useState, useEffect } from 'react'
import { Note, Visualization } from '@/types'
import ConceptMap from './ConceptMap'
import ThemeChart from './ThemeChart'
import PragmaticFlow from './PragmaticFlow'
import InsightDetails from './InsightDetails'
import { Sparkles, Network, TrendingUp } from 'lucide-react'

interface InsightVisualizerProps {
  note: Note
}

export default function InsightVisualizer({ note }: InsightVisualizerProps) {
  const [visualization, setVisualization] = useState<Visualization | null>(null)
  const [loading, setLoading] = useState(true)

  useEffect(() => {
    fetchVisualization()
  }, [note.id])

  const fetchVisualization = async () => {
    setLoading(true)
    try {
      const response = await fetch(`/api/notes/${note.id}/visualize`)
      const data = await response.json()
      setVisualization(data)
    } catch (error) {
      console.error('Error fetching visualization:', error)
    } finally {
      setLoading(false)
    }
  }

  if (loading) {
    return (
      <div className="philosophy-gradient rounded-2xl p-12 text-center">
        <p className="text-xl text-gray-300">Extracting visual insights...</p>
      </div>
    )
  }

  return (
    <div className="space-y-6">
      {/* Note Content */}
      <div className="philosophy-gradient rounded-2xl p-6">
        <h2 className="text-3xl font-bold mb-4">{note.title}</h2>
        <div className="prose prose-invert max-w-none">
          <p className="text-gray-300 whitespace-pre-wrap leading-relaxed">{note.content}</p>
        </div>
        <div className="mt-4 flex items-center gap-2 text-sm text-gray-400">
          <span>{new Date(note.created_at).toLocaleString()}</span>
          {note.insights?.insight_score && (
            <span className="ml-auto px-3 py-1 bg-philosophy-glow/20 rounded-full">
              Insight Score: {(note.insights.insight_score * 100).toFixed(0)}%
            </span>
          )}
        </div>
      </div>

      {/* Insights Overview */}
      {note.insights && (
        <InsightDetails insights={note.insights} />
      )}

      {/* Visualizations */}
      {visualization && (
        <>
          {/* Concept Map */}
          {visualization.concept_map && visualization.concept_map.nodes.length > 0 && (
            <div className="philosophy-gradient rounded-2xl p-6">
              <h3 className="text-2xl font-bold mb-4 flex items-center gap-2">
                <Network className="w-6 h-6" />
                Concept Network
              </h3>
              <ConceptMap conceptMap={visualization.concept_map} />
            </div>
          )}

          {/* Theme Distribution */}
          {visualization.theme_distribution && visualization.theme_distribution.length > 0 && (
            <div className="philosophy-gradient rounded-2xl p-6">
              <h3 className="text-2xl font-bold mb-4 flex items-center gap-2">
                <TrendingUp className="w-6 h-6" />
                Theme Distribution
              </h3>
              <ThemeChart data={visualization.theme_distribution} />
            </div>
          )}

          {/* Pragmatic Flow */}
          {visualization.pragmatic_flow && (
            <div className="philosophy-gradient rounded-2xl p-6">
              <h3 className="text-2xl font-bold mb-4 flex items-center gap-2">
                <Sparkles className="w-6 h-6" />
                Pragmatic Applications
              </h3>
              <PragmaticFlow flow={visualization.pragmatic_flow} />
            </div>
          )}
        </>
      )}
    </div>
  )
}

