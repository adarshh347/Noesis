/**
 * BlockEditor - TipTap-based editor for a single block
 * Supports version stacking and Thinker Mode invocation
 */
'use client';

import { useEditor, EditorContent } from '@tiptap/react';
import StarterKit from '@tiptap/starter-kit';
import Placeholder from '@tiptap/extension-placeholder';
import Typography from '@tiptap/extension-typography';
import { useEffect, useState } from 'react';
import { Sparkles, History, MoreVertical } from 'lucide-react';
import type { Block } from '@/lib/stores/noesis-store';
import { useNoesisStore } from '@/lib/stores/noesis-store';

interface BlockEditorProps {
    block: Block;
    onUpdate: (content: string) => void;
    onInvokeThinker: () => void;
    isActive?: boolean;
}

export function BlockEditor({
    block,
    onUpdate,
    onInvokeThinker,
    isActive = false,
}: BlockEditorProps) {
    const [isHovered, setIsHovered] = useState(false);
    const { setSelectedBlock } = useNoesisStore();

    const editor = useEditor({
        extensions: [
            StarterKit.configure({
                heading: {
                    levels: [1, 2, 3],
                },
            }),
            Placeholder.configure({
                placeholder: 'Begin your philosophical inquiry...',
            }),
            Typography,
        ],
        content: block.active_version?.content || '',
        editorProps: {
            attributes: {
                class: 'editor-content prose focus:outline-none',
            },
        },
        onUpdate: ({ editor }) => {
            onUpdate(editor.getHTML());
        },
        onFocus: () => {
            setSelectedBlock(block.id);
        },
    });

    // Update editor content when active version changes
    useEffect(() => {
        if (editor && block.active_version) {
            const currentContent = editor.getHTML();
            const newContent = block.active_version.content;

            if (currentContent !== newContent) {
                editor.commands.setContent(newContent);
            }
        }
    }, [block.active_version, editor]);

    if (!editor) {
        return null;
    }

    const isAIGenerated = block.active_version?.author_type?.startsWith('system_');
    const versionCount = block.version_count || 1;

    return (
        <div
            className={`block ${isActive ? 'block-active' : ''} group`}
            onMouseEnter={() => setIsHovered(true)}
            onMouseLeave={() => setIsHovered(false)}
        >
            {/* Block Controls - Receding UI */}
            <div className="block-controls">
                <div className="flex flex-col gap-2">
                    {/* Phi Symbol - Invoke Thinker Mode */}
                    <button
                        onClick={onInvokeThinker}
                        className="phi-symbol hover:scale-110 transition-transform"
                        title="Invoke Thinker Mode (Φ)"
                        aria-label="Invoke Thinker Mode"
                    >
                        Φ
                    </button>

                    {/* Version History */}
                    {versionCount > 1 && (
                        <button
                            onClick={() => {
                                useNoesisStore.getState().setSelectedBlock(block.id);
                                useNoesisStore.getState().toggleVersionHistory();
                            }}
                            className="text-[var(--text-muted)] hover:text-[var(--accent-amber)] transition-colors"
                            title={`${versionCount} versions`}
                            aria-label="View version history"
                        >
                            <History size={18} />
                        </button>
                    )}

                    {/* More Options */}
                    <button
                        className="text-[var(--text-muted)] hover:text-[var(--text-secondary)] transition-colors opacity-0 group-hover:opacity-100"
                        title="More options"
                        aria-label="More options"
                    >
                        <MoreVertical size={18} />
                    </button>
                </div>
            </div>

            {/* Version Badge */}
            {isAIGenerated && block.active_version && (
                <div className="mb-2 flex items-center gap-2">
                    <span className="version-badge version-badge-ai">
                        <Sparkles size={12} className="mr-1" />
                        {block.active_version.author_type?.replace('system_', '') || 'AI'}
                    </span>
                    {block.active_version.transform_intent && (
                        <span className="version-badge">
                            {block.active_version.transform_intent}
                        </span>
                    )}
                </div>
            )}

            {/* Editor */}
            <EditorContent editor={editor} />

            {/* Version Indicator */}
            {versionCount > 1 && (
                <div className="mt-2 text-xs text-[var(--text-muted)] font-sans">
                    v{block.active_version?.version_number || 1} of {versionCount}
                </div>
            )}
        </div>
    );
}
