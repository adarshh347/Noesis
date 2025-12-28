/**
 * VersionHistoryPanel - Shows version history for the selected block
 * Allows navigating through and activating previous versions
 */
'use client';

import { useEffect, useState } from 'react';
import { X, History, Sparkles, User, ChevronLeft, ChevronRight, Check } from 'lucide-react';
import { useNoesisStore, BlockVersion } from '@/lib/stores/noesis-store';
import { blockApi } from '@/lib/api/client';

export function VersionHistoryPanel() {
    const {
        isVersionHistoryOpen,
        toggleVersionHistory,
        selectedBlockId,
        currentDocument,
    } = useNoesisStore();

    const [versions, setVersions] = useState<BlockVersion[]>([]);
    const [loading, setLoading] = useState(false);
    const [error, setError] = useState<string | null>(null);
    const [activating, setActivating] = useState<string | null>(null);

    // Get the selected block
    const selectedBlock = currentDocument?.blocks?.find(b => b.id === selectedBlockId);

    // Fetch versions when panel opens
    useEffect(() => {
        if (isVersionHistoryOpen && selectedBlockId) {
            fetchVersions();
        }
    }, [isVersionHistoryOpen, selectedBlockId]);

    const fetchVersions = async () => {
        if (!selectedBlockId) return;

        try {
            setLoading(true);
            setError(null);
            const data = await blockApi.getVersions(selectedBlockId);
            // Sort by version number descending (newest first)
            setVersions(data.sort((a, b) => b.version_number - a.version_number));
        } catch (err: any) {
            setError(err.message || 'Failed to load versions');
        } finally {
            setLoading(false);
        }
    };

    const handleActivate = async (version: BlockVersion) => {
        if (!selectedBlockId || version.is_active) return;

        try {
            setActivating(version.id);
            await blockApi.activateVersion(selectedBlockId, version.id);

            // Update the store with new active version
            useNoesisStore.getState().updateBlock(selectedBlockId, {
                active_version: { ...version, is_active: true },
            });

            // Refresh versions list
            await fetchVersions();
        } catch (err: any) {
            setError(err.message || 'Failed to activate version');
        } finally {
            setActivating(null);
        }
    };

    const formatDate = (dateString: string) => {
        const date = new Date(dateString);
        return date.toLocaleDateString('en-US', {
            month: 'short',
            day: 'numeric',
            hour: '2-digit',
            minute: '2-digit',
        });
    };

    const getAuthorLabel = (authorType: string) => {
        if (authorType.startsWith('system_')) {
            return authorType.replace('system_', '').toUpperCase();
        }
        return authorType.toUpperCase();
    };

    const isAI = (authorType: string) => authorType.startsWith('system_');

    if (!isVersionHistoryOpen) return null;

    return (
        <div className="fixed inset-0 z-50 flex items-center justify-end">
            {/* Backdrop */}
            <div
                className="absolute inset-0 bg-black/30 backdrop-blur-sm"
                onClick={toggleVersionHistory}
            />

            {/* Panel */}
            <div className="relative w-full max-w-md h-full bg-[var(--bg-primary)] border-l border-[var(--border-subtle)] shadow-xl overflow-hidden flex flex-col">
                {/* Header */}
                <div className="flex items-center justify-between p-4 border-b border-[var(--border-subtle)]">
                    <div className="flex items-center gap-2">
                        <History size={20} className="text-[var(--accent-amber)]" />
                        <h2 className="text-lg font-serif font-semibold">Version History</h2>
                    </div>
                    <button
                        onClick={toggleVersionHistory}
                        className="p-2 hover:bg-[var(--bg-secondary)] rounded-md transition-colors"
                        aria-label="Close version history"
                    >
                        <X size={18} />
                    </button>
                </div>

                {/* Block Info */}
                {selectedBlock && (
                    <div className="px-4 py-3 bg-[var(--bg-secondary)] border-b border-[var(--border-subtle)]">
                        <p className="text-sm text-[var(--text-muted)] font-sans">
                            Block #{selectedBlock.position_index + 1} • {versions.length} versions
                        </p>
                    </div>
                )}

                {/* Content */}
                <div className="flex-1 overflow-y-auto p-4 space-y-3">
                    {loading && (
                        <div className="text-center py-8">
                            <div className="animate-spin rounded-full h-8 w-8 border-2 border-[var(--accent-amber)] border-t-transparent mx-auto"></div>
                            <p className="mt-2 text-sm text-[var(--text-muted)]">Loading versions...</p>
                        </div>
                    )}

                    {error && (
                        <div className="text-center py-8">
                            <p className="text-red-500">{error}</p>
                            <button
                                onClick={fetchVersions}
                                className="mt-2 btn btn-secondary text-sm"
                            >
                                Retry
                            </button>
                        </div>
                    )}

                    {!loading && !error && versions.length === 0 && (
                        <div className="text-center py-8">
                            <p className="text-[var(--text-muted)]">No versions found</p>
                        </div>
                    )}

                    {!loading && !error && versions.map((version) => (
                        <div
                            key={version.id}
                            className={`
                                relative p-4 rounded-lg border transition-all cursor-pointer
                                ${version.is_active
                                    ? 'border-[var(--accent-amber)] bg-[var(--accent-amber)]/10'
                                    : 'border-[var(--border-subtle)] hover:border-[var(--border-emphasis)] hover:bg-[var(--bg-secondary)]'
                                }
                            `}
                            onClick={() => handleActivate(version)}
                        >
                            {/* Version Header */}
                            <div className="flex items-center justify-between mb-2">
                                <div className="flex items-center gap-2">
                                    <span className="text-sm font-sans font-medium text-[var(--text-primary)]">
                                        v{version.version_number}
                                    </span>

                                    {/* Author Badge */}
                                    <span className={`
                                        inline-flex items-center gap-1 px-2 py-0.5 rounded-full text-xs font-sans
                                        ${isAI(version.author_type)
                                            ? 'bg-[var(--accent-amber)]/20 text-[var(--accent-amber)]'
                                            : 'bg-[var(--sepia)] text-[var(--charcoal)]'
                                        }
                                    `}>
                                        {isAI(version.author_type)
                                            ? <Sparkles size={10} />
                                            : <User size={10} />
                                        }
                                        {getAuthorLabel(version.author_type)}
                                    </span>

                                    {/* Transform Intent */}
                                    {version.transform_intent && (
                                        <span className="px-2 py-0.5 bg-[var(--bg-secondary)] text-[var(--text-muted)] rounded text-xs font-sans">
                                            {version.transform_intent}
                                        </span>
                                    )}
                                </div>

                                {/* Active Indicator */}
                                {version.is_active && (
                                    <span className="flex items-center gap-1 text-xs text-[var(--accent-amber)] font-sans">
                                        <Check size={14} />
                                        Active
                                    </span>
                                )}

                                {/* Loading indicator when activating */}
                                {activating === version.id && (
                                    <div className="animate-spin rounded-full h-4 w-4 border-2 border-[var(--accent-amber)] border-t-transparent"></div>
                                )}
                            </div>

                            {/* Content Preview */}
                            <div
                                className="text-sm text-[var(--text-secondary)] line-clamp-3 font-serif"
                                dangerouslySetInnerHTML={{
                                    __html: version.content.substring(0, 200) + (version.content.length > 200 ? '...' : '')
                                }}
                            />

                            {/* Timestamp */}
                            <p className="mt-2 text-xs text-[var(--text-muted)] font-sans">
                                {formatDate(version.created_at)}
                            </p>
                        </div>
                    ))}
                </div>

                {/* Footer with navigation hint */}
                <div className="px-4 py-3 border-t border-[var(--border-subtle)] bg-[var(--bg-secondary)]">
                    <p className="text-xs text-[var(--text-muted)] font-sans text-center">
                        Click on a version to make it active
                    </p>
                </div>
            </div>
        </div>
    );
}
