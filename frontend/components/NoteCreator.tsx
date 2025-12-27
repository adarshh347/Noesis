'use client'

import { useState } from 'react'
import { Plus, Loader2 } from 'lucide-react'
import { Note } from '@/types'

interface NoteCreatorProps {
  onNoteCreated: (note: Note) => void
}

export default function NoteCreator({ onNoteCreated }: NoteCreatorProps) {
  const [content, setContent] = useState('')
  const [title, setTitle] = useState('')
  const [tags, setTags] = useState('')
  const [loading, setLoading] = useState(false)

  const handleSubmit = async (e: React.FormEvent) => {
    e.preventDefault()
    if (!content.trim()) return

    setLoading(true)
    try {
      const response = await fetch('/api/notes', {
        method: 'POST',
        headers: {
          'Content-Type': 'application/json',
        },
        body: JSON.stringify({
          content: content.trim(),
          title: title.trim() || undefined,
          tags: tags.split(',').map(t => t.trim()).filter(Boolean),
        }),
      })

      if (!response.ok) throw new Error('Failed to create note')

      const newNote = await response.json()
      onNoteCreated(newNote)
      
      // Reset form
      setContent('')
      setTitle('')
      setTags('')
    } catch (error) {
      console.error('Error creating note:', error)
      alert('Failed to create note. Please try again.')
    } finally {
      setLoading(false)
    }
  }

  return (
    <div className="philosophy-gradient rounded-2xl p-6 card-hover">
      <h2 className="text-2xl font-bold mb-4 flex items-center gap-2">
        <Plus className="w-6 h-6" />
        New Philosophical Note
      </h2>
      
      <form onSubmit={handleSubmit} className="space-y-4">
        <div>
          <label className="block text-sm font-medium mb-2">Title (optional)</label>
          <input
            type="text"
            value={title}
            onChange={(e) => setTitle(e.target.value)}
            className="w-full bg-philosophy-dark/50 border border-philosophy-light rounded-lg px-4 py-2 focus:outline-none focus:border-philosophy-glow"
            placeholder="Give your thought a title..."
          />
        </div>
        
        <div>
          <label className="block text-sm font-medium mb-2">Your Philosophical Thought</label>
          <textarea
            value={content}
            onChange={(e) => setContent(e.target.value)}
            rows={8}
            className="w-full bg-philosophy-dark/50 border border-philosophy-light rounded-lg px-4 py-2 focus:outline-none focus:border-philosophy-glow resize-none"
            placeholder="Pour your philosophical insights here... Let your thoughts flow freely..."
            required
          />
        </div>
        
        <div>
          <label className="block text-sm font-medium mb-2">Tags (comma-separated)</label>
          <input
            type="text"
            value={tags}
            onChange={(e) => setTags(e.target.value)}
            className="w-full bg-philosophy-dark/50 border border-philosophy-light rounded-lg px-4 py-2 focus:outline-none focus:border-philosophy-glow"
            placeholder="pragmatism, philosophy, culture..."
          />
        </div>
        
        <button
          type="submit"
          disabled={loading || !content.trim()}
          className="w-full bg-philosophy-glow hover:bg-philosophy-glow/80 text-white font-semibold py-3 rounded-lg transition-all flex items-center justify-center gap-2 disabled:opacity-50 disabled:cursor-not-allowed glow-effect"
        >
          {loading ? (
            <>
              <Loader2 className="w-5 h-5 animate-spin" />
              Extracting Insights...
            </>
          ) : (
            <>
              <Plus className="w-5 h-5" />
              Capture Thought
            </>
          )}
        </button>
      </form>
    </div>
  )
}

