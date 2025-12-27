"""
Insight Extractor Service
Extracts and structures philosophical insights from notes
"""

from typing import Dict, List
from services.ai_service import AIService


class InsightExtractor:
    """Extracts structured insights from philosophical notes"""
    
    def __init__(self):
        self.ai_service = AIService()
    
    async def extract_insights(self, content: str) -> Dict:
        """
        Extract structured insights from philosophical content
        Returns a dictionary with themes, concepts, visualizations, etc.
        """
        # Get AI analysis
        analysis = await self.ai_service.analyze_philosophical_text(content)
        
        # Structure insights
        insights = {
            "themes": analysis.get("themes", []),
            "concepts": analysis.get("concepts", []),
            "arguments": analysis.get("arguments", []),
            "connections": analysis.get("connections", []),
            "pragmatic_applications": analysis.get("pragmatic_applications", []),
            "visual_metaphors": analysis.get("visual_metaphors", []),
            "concept_map": self._build_concept_map(analysis),
            "insight_score": self._calculate_insight_score(analysis)
        }
        
        return insights
    
    def _build_concept_map(self, analysis: Dict) -> Dict:
        """Build a concept map structure for visualization"""
        concepts = analysis.get("concepts", [])
        themes = analysis.get("themes", [])
        
        nodes = []
        edges = []
        
        # Add theme nodes
        for i, theme in enumerate(themes):
            nodes.append({
                "id": f"theme_{i}",
                "label": theme,
                "type": "theme",
                "size": 20
            })
        
        # Add concept nodes
        for i, concept in enumerate(concepts):
            nodes.append({
                "id": f"concept_{i}",
                "label": concept,
                "type": "concept",
                "size": 15
            })
        
        # Create edges between themes and concepts
        for i, theme in enumerate(themes):
            for j, concept in enumerate(concepts):
                # Simple heuristic: connect if concept appears in theme or vice versa
                if concept.lower() in theme.lower() or theme.lower() in concept.lower():
                    edges.append({
                        "source": f"theme_{i}",
                        "target": f"concept_{j}",
                        "strength": 0.5
                    })
        
        return {
            "nodes": nodes,
            "edges": edges
        }
    
    def _calculate_insight_score(self, analysis: Dict) -> float:
        """Calculate a score indicating the depth/richness of insights"""
        themes_count = len(analysis.get("themes", []))
        concepts_count = len(analysis.get("concepts", []))
        applications_count = len(analysis.get("pragmatic_applications", []))
        
        # Simple scoring: more themes, concepts, and applications = higher score
        score = (themes_count * 2 + concepts_count * 1.5 + applications_count * 2) / 10
        return min(score, 1.0)  # Cap at 1.0
    
    async def generate_visualization(self, note_data: Dict) -> Dict:
        """Generate visualization data for a note"""
        insights = note_data.get("insights", {})
        
        visualization = {
            "concept_map": insights.get("concept_map", {}),
            "theme_distribution": self._get_theme_distribution(insights),
            "pragmatic_flow": self._get_pragmatic_flow(insights),
            "temporal_connections": self._get_temporal_connections(note_data, insights)
        }
        
        return visualization
    
    def _get_theme_distribution(self, insights: Dict) -> List[Dict]:
        """Get theme distribution data for charts"""
        themes = insights.get("themes", [])
        return [
            {"theme": theme, "weight": 1.0, "connections": len(insights.get("concepts", []))}
            for theme in themes
        ]
    
    def _get_pragmatic_flow(self, insights: Dict) -> Dict:
        """Get pragmatic application flow structure"""
        applications = insights.get("pragmatic_applications", [])
        themes = insights.get("themes", [])
        
        return {
            "themes": themes,
            "applications": applications,
            "connections": [
                {"from": theme, "to": app}
                for theme in themes
                for app in applications
            ]
        }
    
    def _get_temporal_connections(self, note_data: Dict, insights: Dict) -> Dict:
        """Get temporal/evolutionary connections (for future notes)"""
        return {
            "created_at": note_data.get("created_at"),
            "themes": insights.get("themes", []),
            "future_connections": []  # Will be populated as more notes are added
        }

