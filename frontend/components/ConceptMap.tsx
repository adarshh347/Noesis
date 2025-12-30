'use client'

import { useEffect, useRef, useState } from 'react'
import { ConceptMap } from '@/types'
import dynamic from 'next/dynamic'

// Dynamically import to avoid SSR issues
const ForceGraph2D = dynamic(() => import('react-force-graph-2d'), {
  ssr: false,
  loading: () => <div className="w-full h-[400px] flex items-center justify-center text-gray-400">Loading visualization...</div>
})

interface ConceptMapProps {
  conceptMap: ConceptMap
}

export default function ConceptMapComponent({ conceptMap }: ConceptMapProps) {
  const graphRef = useRef<any>()
  const [error, setError] = useState(false)

  useEffect(() => {
    if (graphRef.current && conceptMap.nodes.length > 0) {
      try {
        graphRef.current.d3Force('charge')?.strength(-300)
        graphRef.current.d3Force('link')?.distance(100)
      } catch (e) {
        console.error('Error setting up graph forces:', e)
      }
    }
  }, [conceptMap])

  if (!conceptMap.nodes || conceptMap.nodes.length === 0) {
    return (
      <div className="w-full h-[400px] bg-philosophy-dark/50 rounded-lg flex items-center justify-center">
        <p className="text-gray-400">No concept map available</p>
      </div>
    )
  }

  if (error) {
    // Fallback: Simple list view
    return (
      <div className="w-full h-[400px] bg-philosophy-dark/50 rounded-lg p-6 overflow-y-auto">
        <div className="space-y-4">
          <div>
            <h4 className="text-lg font-semibold mb-2 text-philosophy-glow">Themes</h4>
            <div className="flex flex-wrap gap-2">
              {conceptMap.nodes.filter(n => n.type === 'theme').map((node, idx) => (
                <span key={idx} className="px-3 py-1 bg-philosophy-glow/20 rounded-lg">
                  {node.label}
                </span>
              ))}
            </div>
          </div>
          <div>
            <h4 className="text-lg font-semibold mb-2 text-philosophy-light">Concepts</h4>
            <div className="flex flex-wrap gap-2">
              {conceptMap.nodes.filter(n => n.type === 'concept').map((node, idx) => (
                <span key={idx} className="px-3 py-1 bg-philosophy-light/20 rounded-lg">
                  {node.label}
                </span>
              ))}
            </div>
          </div>
        </div>
      </div>
    )
  }

  const graphData = {
    nodes: conceptMap.nodes.map(node => ({
      ...node,
      color: node.type === 'theme' ? '#e94560' : '#533483',
    })),
    links: (conceptMap.edges || []).map(edge => ({
      source: edge.source,
      target: edge.target,
      value: edge.strength || 0.5,
    })),
  }

  return (
    <div className="w-full h-[400px] bg-philosophy-dark/50 rounded-lg overflow-hidden">
      <ForceGraph2D
        ref={graphRef}
        graphData={graphData}
        nodeLabel={(node: any) => node.label}
        nodeColor={(node: any) => node.color}
        linkColor={() => 'rgba(255, 255, 255, 0.2)'}
        linkWidth={2}
        nodeVal={(node: any) => node.size || 10}
        backgroundColor="transparent"
        cooldownTicks={100}
        onEngineStop={() => {
          try {
            graphRef.current?.zoomToFit(400)
          } catch (e) {
            console.error('Error zooming to fit:', e)
            setError(true)
          }
        }}
      />
    </div>
  )
}

