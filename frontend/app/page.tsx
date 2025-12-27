'use client'

import { useState, useEffect } from 'react'
import NoteList from '@/components/NoteList'
import NoteCreator from '@/components/NoteCreator'
import InsightVisualizer from '@/components/InsightVisualizer'
import { Note } from '@/types'

export default function Home() {
  const [notes, setNotes] = useState<Note[]>([])
  const [selectedNote, setSelectedNote] = useState<Note | null>(null)
  const [loading, setLoading] = useState(true)

  useEffect(() => {
    fetchNotes()
  }, [])

  const fetchNotes = async () => {
    try {
      const response = await fetch('/api/notes')
      const data = await response.json()
      setNotes(data)
      if (data.length > 0 && !selectedNote) {
        setSelectedNote(data[0])
      }
    } catch (error) {
      console.error('Error fetching notes:', error)
    } finally {
      setLoading(false)
    }
  }

  const handleNoteCreated = (newNote: Note) => {
    setNotes([newNote, ...notes])
    setSelectedNote(newNote)
  }

  return (
    <main className="min-h-screen p-8">
      <div className="max-w-7xl mx-auto">
        {/* Header */}
        <header className="mb-12 text-center">
          <h1 className="text-6xl font-bold mb-4 bg-gradient-to-r from-philosophy-glow to-philosophy-light bg-clip-text text-transparent">
            Weltanschauung
          </h1>
          <p className="text-xl text-gray-400 italic">
            Philosophy Beyond Text • Converting Thoughts into Visible Insights
          </p>
        </header>

        <div className="grid grid-cols-1 lg:grid-cols-3 gap-8">
          {/* Left Column: Note Creator & List */}
          <div className="lg:col-span-1 space-y-6">
            <NoteCreator onNoteCreated={handleNoteCreated} />
            <NoteList 
              notes={notes} 
              selectedNote={selectedNote}
              onSelectNote={setSelectedNote}
              loading={loading}
            />
          </div>

          {/* Right Column: Visualizations */}
          <div className="lg:col-span-2">
            {selectedNote ? (
              <InsightVisualizer note={selectedNote} />
            ) : (
              <div className="philosophy-gradient rounded-2xl p-12 text-center">
                <p className="text-2xl text-gray-300">
                  Select a note or create a new one to see insights
                </p>
              </div>
            )}
          </div>
        </div>
      </div>
    </main>
  )
}

