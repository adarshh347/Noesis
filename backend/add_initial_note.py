"""
Script to add the initial philosophical note
"""

import json
import sys
from pathlib import Path
from datetime import datetime

# Add parent directory to path
sys.path.append(str(Path(__file__).parent))

from services.insight_extractor import InsightExtractor
import asyncio

NOTES_DIR = Path(__file__).parent.parent / "notes"
NOTES_DIR.mkdir(exist_ok=True)


async def add_initial_note():
    """Add the first philosophical note"""
    
    note_content = """I ain't gonna ever pursue philosophy as a medium to win over debates with metaphysical salutes(this i have done for two years(21-23 phase)
and that is why most philosophers pursue philosophy

and it's for vain

the world has pragmatically evolved
Humans have exponential pragmatic responsibilities and aspirations as they had a thousand year ago

so each task we do need a pragmatic twist and a good amount of pragmatism ratio
that is where philosophy has been trailing behind
therefore apart from the cherry picks of existentialism much of the abstract philosophy goes into vain

that is not what i want to do

I'm sure that i'm not going to pursue philosophy as a matter of convincement among the group of senators to win the debate or write a metaphysical doctrine cancelling the opponent

But, I don't exactly know how then I pursue philosophy
what i'm pretty much sure that it has a lot of potentials to contribute to the human culture

but that will only happen when we will stop putting the final endpoints at the text as a hallmark of philosophy

We have to move the interface of philosophy beyond the text
one of the motto of this application to build will be that
we will convert my good ideas and your reasoning capabilities to enhance search deeper meaningful insights
exponentially extract them show in beautiful uis, graphs, ai generated responses"""

    note_id = datetime.now().strftime("%Y%m%d_%H%M%S")
    created_at = datetime.now().isoformat()
    
    title = "Philosophy Beyond Text: A Pragmatic Approach"
    
    # Extract insights
    extractor = InsightExtractor()
    insights = await extractor.extract_insights(note_content)
    
    note_data = {
        "id": note_id,
        "title": title,
        "content": note_content,
        "tags": ["pragmatism", "philosophy", "culture", "visual-philosophy", "applied-philosophy"],
        "created_at": created_at,
        "insights": insights
    }
    
    # Save to file
    note_file = NOTES_DIR / f"{note_id}.json"
    with open(note_file, "w", encoding="utf-8") as f:
        json.dump(note_data, f, indent=2, ensure_ascii=False)
    
    print(f"✓ Initial note created: {note_file}")
    print(f"  Title: {title}")
    print(f"  Themes extracted: {len(insights.get('themes', []))}")
    print(f"  Concepts extracted: {len(insights.get('concepts', []))}")
    print(f"  Insight score: {insights.get('insight_score', 0):.2f}")


if __name__ == "__main__":
    asyncio.run(add_initial_note())

