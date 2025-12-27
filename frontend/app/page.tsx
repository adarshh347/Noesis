'use client';

import { useState, useEffect } from 'react';
import { FileText, Plus, Folder } from 'lucide-react';
import { useRouter } from 'next/navigation';
import { documentApi } from '@/lib/api/client';
import type { Document } from '@/lib/stores/noesis-store';

export default function Home() {
  const router = useRouter();
  const [documents, setDocuments] = useState<Document[]>([]);
  const [loading, setLoading] = useState(true);
  const [isCreating, setIsCreating] = useState(false);

  useEffect(() => {
    loadDocuments();
  }, []);

  const loadDocuments = async () => {
    try {
      const docs = await documentApi.list('/');
      setDocuments(docs);
    } catch (error) {
      console.error('Error loading documents:', error);
    } finally {
      setLoading(false);
    }
  };

  const handleCreateDocument = async () => {
    setIsCreating(true);
    try {
      const newDoc = await documentApi.create({
        title: 'Untitled Document',
        tags: [],
        folder_path: '/',
      });
      router.push(`/editor/${newDoc.id}`);
    } catch (error) {
      console.error('Error creating document:', error);
      setIsCreating(false);
    }
  };

  return (
    <main className="min-h-screen bg-[var(--bg-primary)]">
      {/* Header */}
      <header className="border-b border-[var(--border-subtle)] bg-[var(--bg-primary)]">
        <div className="max-w-6xl mx-auto px-6 py-8">
          <h1 className="text-5xl font-serif font-semibold mb-3 text-[var(--text-primary)]">
            Noesis
          </h1>
          <p className="text-lg text-[var(--text-secondary)] font-serif italic">
            The Creative Philosophy Studio
          </p>
          <p className="text-sm text-[var(--text-muted)] font-sans mt-2">
            Writing as Thinking • Every paragraph is a malleable object with infinite versions
          </p>
        </div>
      </header>

      {/* Main Content */}
      <div className="max-w-6xl mx-auto px-6 py-12">
        {/* Create Button */}
        <div className="mb-8">
          <button
            onClick={handleCreateDocument}
            disabled={isCreating}
            className="btn btn-primary flex items-center gap-2"
          >
            <Plus size={20} />
            {isCreating ? 'Creating...' : 'New Document'}
          </button>
        </div>

        {/* Documents List */}
        {loading ? (
          <div className="text-center py-16">
            <FileText size={48} className="mx-auto mb-4 text-[var(--text-muted)]" />
            <p className="text-[var(--text-secondary)] font-sans">Loading documents...</p>
          </div>
        ) : documents.length === 0 ? (
          <div className="text-center py-16 bg-[var(--bg-secondary)] rounded-lg">
            <FileText size={64} className="mx-auto mb-4 text-[var(--text-muted)]" />
            <h2 className="text-2xl font-serif mb-2 text-[var(--text-primary)]">
              No documents yet
            </h2>
            <p className="text-[var(--text-secondary)] font-sans mb-6">
              Create your first philosophical document to begin
            </p>
            <button
              onClick={handleCreateDocument}
              disabled={isCreating}
              className="btn btn-primary"
            >
              <Plus size={20} className="mr-2" />
              Create First Document
            </button>
          </div>
        ) : (
          <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-6">
            {documents.map((doc) => (
              <button
                key={doc.id}
                onClick={() => router.push(`/editor/${doc.id}`)}
                className="card card-hover p-6 text-left transition-all"
              >
                <div className="flex items-start gap-3 mb-3">
                  <FileText size={24} className="text-[var(--accent-amber)] flex-shrink-0 mt-1" />
                  <div className="flex-1 min-w-0">
                    <h3 className="font-serif text-xl mb-1 truncate text-[var(--text-primary)]">
                      {doc.title}
                    </h3>
                    <p className="text-sm text-[var(--text-muted)] font-sans">
                      {doc.block_count || 0} blocks
                    </p>
                  </div>
                </div>

                {doc.tags && doc.tags.length > 0 && (
                  <div className="flex flex-wrap gap-2 mb-3">
                    {doc.tags.slice(0, 3).map((tag) => (
                      <span
                        key={tag}
                        className="px-2 py-1 bg-[var(--sepia)] text-[var(--charcoal)] rounded text-xs font-sans"
                      >
                        {tag}
                      </span>
                    ))}
                    {doc.tags.length > 3 && (
                      <span className="px-2 py-1 text-[var(--text-muted)] text-xs font-sans">
                        +{doc.tags.length - 3} more
                      </span>
                    )}
                  </div>
                )}

                <div className="flex items-center gap-2 text-xs text-[var(--text-muted)] font-sans">
                  <Folder size={14} />
                  <span>{doc.folder_path}</span>
                </div>

                <div className="mt-3 text-xs text-[var(--text-muted)] font-sans">
                  Updated {new Date(doc.updated_at).toLocaleDateString()}
                </div>
              </button>
            ))}
          </div>
        )}
      </div>

      {/* Footer */}
      <footer className="border-t border-[var(--border-subtle)] mt-16">
        <div className="max-w-6xl mx-auto px-6 py-8 text-center">
          <p className="text-sm text-[var(--text-muted)] font-sans">
            Noesis • Digital Monastery for Rigorous Intellectual Creation
          </p>
        </div>
      </footer>
    </main>
  );
}


