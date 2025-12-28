/**
 * DocumentEditor - Main editor component
 * Manages multiple blocks and coordinates the editing experience
 */
'use client';

import { useEffect, useState } from 'react';
import { Plus, Save, FileText } from 'lucide-react';
import { BlockEditor } from './BlockEditor';
import { ThinkerDialog } from './ThinkerDialog';
import { useNoesisStore } from '@/lib/stores/noesis-store';
import { documentApi, blockApi } from '@/lib/api/client';

interface DocumentEditorProps {
    documentId: string;
}

export function DocumentEditor({ documentId }: DocumentEditorProps) {
    const {
        currentDocument,
        setCurrentDocument,
        selectedBlockId,
        openThinkerDialog,
    } = useNoesisStore();

    const [isLoading, setIsLoading] = useState(true);
    const [isSaving, setIsSaving] = useState(false);
    const [error, setError] = useState<string | null>(null);

    // Load document
    useEffect(() => {
        loadDocument();
    }, [documentId]);

    const loadDocument = async () => {
        try {
            setIsLoading(true);
            const doc = await documentApi.get(documentId);
            setCurrentDocument(doc);
        } catch (err: any) {
            setError(err.message);
        } finally {
            setIsLoading(false);
        }
    };

    const handleAddBlock = async () => {
        if (!currentDocument) return;

        try {
            const newBlock = await blockApi.create({
                document_id: documentId,
                position_index: currentDocument.blocks?.length || 0,
                block_type: 'paragraph',
                initial_content: '<p></p>',  // Must have content for backend validation
            });

            // Reload document to get updated blocks
            await loadDocument();
        } catch (err: any) {
            setError(err.message);
        }
    };

    const handleBlockUpdate = async (blockId: string, content: string) => {
        try {
            // Create new version with updated content
            await blockApi.createVersion(blockId, {
                content,
                author_type: 'user',
            });
        } catch (err: any) {
            console.error('Failed to update block:', err);
        }
    };

    const handleInvokeThinker = (blockId: string) => {
        useNoesisStore.getState().setSelectedBlock(blockId);
        openThinkerDialog();
    };

    if (isLoading) {
        return (
            <div className="flex items-center justify-center h-screen">
                <div className="text-center">
                    <FileText size={48} className="mx-auto mb-4 text-[var(--text-muted)]" />
                    <p className="text-[var(--text-secondary)] font-sans">Loading document...</p>
                </div>
            </div>
        );
    }

    if (error) {
        return (
            <div className="flex items-center justify-center h-screen">
                <div className="text-center">
                    <p className="text-red-600 mb-4">{error}</p>
                    <button onClick={loadDocument} className="btn btn-primary">
                        Retry
                    </button>
                </div>
            </div>
        );
    }

    if (!currentDocument) {
        return null;
    }

    return (
        <div className="min-h-screen bg-[var(--bg-primary)]">
            {/* Header */}
            <header className="sticky top-0 z-10 bg-[var(--bg-primary)]/95 backdrop-blur-sm border-b border-[var(--border-subtle)]">
                <div className="max-w-4xl mx-auto px-6 py-4">
                    <div className="flex items-center justify-between">
                        <div className="flex-1">
                            <input
                                type="text"
                                value={currentDocument.title}
                                onChange={(e) => {
                                    // Update title locally
                                    setCurrentDocument({
                                        ...currentDocument,
                                        title: e.target.value,
                                    });
                                }}
                                onBlur={async (e) => {
                                    // Save title to backend
                                    try {
                                        await documentApi.update(documentId, {
                                            title: e.target.value,
                                        });
                                    } catch (err) {
                                        console.error('Failed to update title:', err);
                                    }
                                }}
                                className="text-3xl font-serif font-semibold bg-transparent border-none outline-none focus:ring-0 w-full"
                                placeholder="Untitled Document"
                            />
                        </div>
                        <div className="flex items-center gap-2">
                            {isSaving && (
                                <span className="text-sm text-[var(--text-muted)] font-sans">
                                    Saving...
                                </span>
                            )}
                            <button
                                onClick={handleAddBlock}
                                className="btn btn-secondary"
                                title="Add block"
                            >
                                <Plus size={18} />
                            </button>
                        </div>
                    </div>

                    {/* Tags */}
                    {currentDocument.tags && currentDocument.tags.length > 0 && (
                        <div className="mt-3 flex flex-wrap gap-2">
                            {currentDocument.tags.map((tag) => (
                                <span
                                    key={tag}
                                    className="px-3 py-1 bg-[var(--sepia)] text-[var(--charcoal)] rounded-full text-sm font-sans"
                                >
                                    {tag}
                                </span>
                            ))}
                        </div>
                    )}
                </div>
            </header>

            {/* Editor Content */}
            <main className="max-w-4xl mx-auto px-6 py-12">
                <div className="space-y-6">
                    {currentDocument.blocks && currentDocument.blocks.length > 0 ? (
                        currentDocument.blocks.map((block) => (
                            <BlockEditor
                                key={block.id}
                                block={block}
                                onUpdate={(content) => handleBlockUpdate(block.id, content)}
                                onInvokeThinker={() => handleInvokeThinker(block.id)}
                                isActive={selectedBlockId === block.id}
                            />
                        ))
                    ) : (
                        <div className="text-center py-16">
                            <p className="text-[var(--text-muted)] font-sans mb-4">
                                No blocks yet. Start writing!
                            </p>
                            <button onClick={handleAddBlock} className="btn btn-primary">
                                <Plus size={18} className="mr-2" />
                                Add First Block
                            </button>
                        </div>
                    )}
                </div>

                {/* Add Block Button (at bottom) */}
                {currentDocument.blocks && currentDocument.blocks.length > 0 && (
                    <div className="mt-8 text-center">
                        <button
                            onClick={handleAddBlock}
                            className="btn btn-ghost text-[var(--text-muted)] hover:text-[var(--text-primary)]"
                        >
                            <Plus size={18} className="mr-2" />
                            Add Block
                        </button>
                    </div>
                )}
            </main>

            {/* Thinker Dialog */}
            <ThinkerDialog />
        </div>
    );
}
