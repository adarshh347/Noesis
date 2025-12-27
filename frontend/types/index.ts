export interface Note {
  id: string
  title: string
  content: string
  tags: string[]
  created_at: string
  insights?: Insights
}

export interface Insights {
  themes?: string[]
  concepts?: string[]
  arguments?: string[]
  connections?: string[]
  pragmatic_applications?: string[]
  visual_metaphors?: string[]
  concept_map?: ConceptMap
  insight_score?: number
}

export interface ConceptMap {
  nodes: ConceptNode[]
  edges: ConceptEdge[]
}

export interface ConceptNode {
  id: string
  label: string
  type: 'theme' | 'concept'
  size: number
}

export interface ConceptEdge {
  source: string
  target: string
  strength: number
}

export interface Visualization {
  concept_map: ConceptMap
  theme_distribution: ThemeDistribution[]
  pragmatic_flow: PragmaticFlow
  temporal_connections: TemporalConnections
}

export interface ThemeDistribution {
  theme: string
  weight: number
  connections: number
}

export interface PragmaticFlow {
  themes: string[]
  applications: string[]
  connections: { from: string; to: string }[]
}

export interface TemporalConnections {
  created_at: string
  themes: string[]
  future_connections: any[]
}

