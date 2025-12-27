'use client'

import { Note } from '@/types'
import { BookOpen, Calendar } from 'lucide-react'

interface NoteListProps {
  notes: Note[]
  selectedNote: Note | null
  onSelectNote: (note: Note) => void
  loading: boolean
}

export default function NoteList({ notes, selectedNote, onSelectNote, loading }: NoteListProps) {
  if (loading) {
    return (
      <div className="philosophy-gradient rounded-2xl p-6">
        <p className="text-gray-400">Loading notes...</p>
      </div>
    )
  }

  if (notes.length === 0) {
    return (
      <div className="philosophy-gradient rounded-2xl p-6">
        <p className="text-gray-400 text-center">No notes yet. Create your first philosophical thought!</p>
      </div>
    )
  }

  return (
    <div className="philosophy-gradient rounded-2xl p-6">
      <h2 className="text-2xl font-bold mb-4 flex items-center gap-2">
        <BookOpen className="w-6 h-6" />
        Your Thoughts
      </h2>
      <div className="space-y-3 max-h-[600px] overflow-y-auto">
        {notes.map((note) => (
          <div
            key={note.id}
            onClick={() => onSelectNote(note)}
            className={`p-4 rounded-lg cursor-pointer transition-all card-hover ${
              selectedNote?.id === note.id
                ? 'bg-philosophy-glow/20 border-2 border-philosophy-glow glow-effect'
                : 'bg-philosophy-dark/50 border border-philosophy-light hover:border-philosophy-glow'
            }`}
          >
            <h3 className="font-semibold text-lg mb-2 line-clamp-2">{note.title}</h3>
            <p className="text-sm text-gray-400 line-clamp-3 mb-3">{note.content}</p>
            <div className="flex items-center justify-between text-xs text-gray-500">
              <div className="flex items-center gap-1">
                <Calendar className="w-3 h-3" />
                {new Date(note.created_at).toLocaleDateString()}
              </div>
              {note.insights?.insight_score && (
                <div className="px-2 py-1 bg-philosophy-glow/20 rounded">
                  Score: {(note.insights.insight_score * 100).toFixed(0)}%
                </div>
              )}
            </div>
            {note.tags.length > 0 && (
              <div className="flex flex-wrap gap-1 mt-2">
                {note.tags.map((tag, idx) => (
                  <span
                    key={idx}
                    className="text-xs px-2 py-1 bg-philosophy-accent/50 rounded"
                  >
                    {tag}
                  </span>
                ))}
              </div>
            )}
          </div>
        ))}
      </div>
    </div>
  )
}

