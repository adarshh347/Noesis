"""
AI Service for philosophical insight extraction and generation
"""

import os
from typing import Dict, List, Optional
from groq import Groq
from dotenv import load_dotenv

load_dotenv()


class AIService:
    """Service for AI-powered philosophical analysis"""
    
    def __init__(self):
        api_key = os.getenv("GROQ_API_KEY")
        if not api_key:
            # Fallback: use a mock mode if no API key
            self.client = None
            self.mock_mode = True
        else:
            self.client = Groq(api_key=api_key)
            self.mock_mode = False
    
    async def analyze_philosophical_text(
        self, 
        text: str, 
        context: Optional[str] = None
    ) -> Dict:
        """
        Analyze philosophical text and extract:
        - Core themes and concepts
        - Key arguments and insights
        - Connections to broader philosophical traditions
        - Pragmatic applications
        """
        if self.mock_mode:
            return self._mock_analysis(text)
        
        prompt = f"""You are a philosophical AI assistant helping to extract and visualize philosophical insights.

Analyze the following philosophical text and provide a structured analysis:

{text}

Provide:
1. Core themes (3-5 main themes)
2. Key concepts (important philosophical concepts mentioned)
3. Arguments (main arguments or positions)
4. Connections (links to philosophical traditions, thinkers, or ideas)
5. Pragmatic applications (how these ideas can be applied practically)
6. Visual metaphors (suggestions for how to visualize these concepts)

Format as JSON with these keys: themes, concepts, arguments, connections, pragmatic_applications, visual_metaphors"""

        try:
            response = self.client.chat.completions.create(
                model="openai/gpt-oss-120b",
                messages=[
                    {"role": "system", "content": "You are a philosophical AI that helps extract and visualize deep insights. Always respond with valid JSON."},
                    {"role": "user", "content": prompt}
                ],
                temperature=0.7,
                max_tokens=2000
            )
            
            import json
            result = response.choices[0].message.content
            # Try to parse JSON from response
            try:
                return json.loads(result)
            except:
                # If not JSON, return structured format
                return {
                    "themes": [],
                    "concepts": [],
                    "arguments": [],
                    "connections": [],
                    "pragmatic_applications": [],
                    "visual_metaphors": [],
                    "raw_analysis": result
                }
        except Exception as e:
            return self._mock_analysis(text)
    
    def _mock_analysis(self, text: str) -> Dict:
        """Mock analysis for when API key is not available"""
        return {
            "themes": ["Pragmatic Philosophy", "Philosophy Beyond Text", "Cultural Contribution"],
            "concepts": ["Pragmatism", "Visual Philosophy", "Applied Philosophy"],
            "arguments": ["Philosophy should move beyond text", "Philosophy needs pragmatic applications"],
            "connections": ["Existentialism", "Pragmatism", "Applied Philosophy"],
            "pragmatic_applications": ["Visual interfaces", "Interactive tools", "Cultural contributions"],
            "visual_metaphors": ["Growing tree of ideas", "Network of concepts", "Flowing river of thought"]
        }
    
    async def generate_insight_expansion(self, theme: str, context: str) -> str:
        """Generate expanded insights on a particular theme"""
        if self.mock_mode:
            return f"Expanded insight on {theme}: This theme connects deeply with the philosophical tradition and offers practical applications."
        
        prompt = f"""Expand on this philosophical theme: {theme}

Context: {context}

Provide a deeper exploration of this theme, connecting it to broader philosophical ideas and practical applications."""

        try:
            response = self.client.chat.completions.create(
                model="openai/gpt-oss-120b",
                messages=[
                    {"role": "system", "content": "You are a philosophical AI that expands on themes with depth and practical relevance."},
                    {"role": "user", "content": prompt}
                ],
                temperature=0.8,
                max_tokens=1000
            )
            return response.choices[0].message.content
        except:
            return f"Expanded insight on {theme}: [AI analysis unavailable]"

