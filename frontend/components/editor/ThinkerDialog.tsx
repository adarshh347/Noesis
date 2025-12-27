/**
 * ThinkerDialog - The Dialectic Wheel
 * Beautiful circular interface for selecting thinkers and transformation intents
 */
'use client';

import { useState, useEffect } from 'react';
import { X, Sparkles, Loader2 } from 'lucide-react';
import { useNoesisStore } from '@/lib/stores/noesis-store';
import { aiApi, type TransformRequest } from '@/lib/api/client';
import { blockApi } from '@/lib/api/client';

interface Thinker {
    id: string;
    name: string;
    description: string;
    style_suggestions: string[];
}

interface Intent {
    id: string;
    description: string;
}

export function ThinkerDialog() {
    const {
        isThinkerDialogOpen,
        closeThinkerDialog,
        selectedBlockId,
        selectedThinker,
        selectedIntent,
        selectedStyle,
        setThinker,
        setIntent,
        setStyle,
        resetThinkerSelection,
        addVersion,
    } = useNoesisStore();

    const [thinkers, setThinkers] = useState<Thinker[]>([]);
    const [intents, setIntents] = useState<Intent[]>([]);
    const [isTransforming, setIsTransforming] = useState(false);
    const [error, setError] = useState<string | null>(null);

    // Load thinkers and intents
    useEffect(() => {
        if (isThinkerDialogOpen) {
            aiApi.getThinkers().then((data) => {
                setThinkers(data.thinkers);
                setIntents(data.intents);
            });
        }
    }, [isThinkerDialogOpen]);

    if (!isThinkerDialogOpen || !selectedBlockId) return null;

    const handleTransform = async () => {
        if (!selectedThinker || !selectedIntent) {
            setError('Please select both a thinker and an intent');
            return;
        }

        setIsTransforming(true);
        setError(null);

        try {
            const request: TransformRequest = {
                block_id: selectedBlockId,
                thinker: selectedThinker,
                intent: selectedIntent as any,
                style: selectedStyle || undefined,
            };

            const response = await aiApi.transform(request);

            // Add the new version to the store
            addVersion(selectedBlockId, {
                id: response.new_version_id,
                block_id: selectedBlockId,
                content: response.transformed_content,
                author_type: `system_${selectedThinker}`,
                transform_intent: selectedIntent,
                transform_params: {
                    thinker: selectedThinker,
                    style: selectedStyle,
                },
                is_active: true,
                version_number: 0, // Will be set by backend
                created_at: new Date().toISOString(),
            });

            // Close dialog and reset
            handleClose();
        } catch (err: any) {
            setError(err.message || 'Transformation failed');
        } finally {
            setIsTransforming(false);
        }
    };

    const handleClose = () => {
        closeThinkerDialog();
        resetThinkerSelection();
        setError(null);
    };

    // Calculate positions for circular layout
    const getThinkerPosition = (index: number, total: number) => {
        const angle = (index / total) * 2 * Math.PI - Math.PI / 2;
        const radius = 120;
        const x = Math.cos(angle) * radius;
        const y = Math.sin(angle) * radius;
        return { x, y };
    };

    const selectedThinkerData = thinkers.find((t) => t.id === selectedThinker);

    return (
        <div className="modal-overlay" onClick={handleClose}>
            <div
                className="modal-content"
                onClick={(e) => e.stopPropagation()}
            >
                {/* Header */}
                <div className="flex items-center justify-between mb-6">
                    <h2 className="text-2xl font-serif">Invoke Thinker Mode</h2>
                    <button
                        onClick={handleClose}
                        className="btn-ghost p-2"
                        aria-label="Close"
                    >
                        <X size={24} />
                    </button>
                </div>

                {/* Thinker Wheel */}
                <div className="mb-8">
                    <h3 className="text-sm font-sans text-[var(--text-secondary)] mb-4 text-center">
                        Select a Philosopher
                    </h3>
                    <div className="thinker-wheel">
                        {/* Center */}
                        <div className="absolute top-1/2 left-1/2 -translate-x-1/2 -translate-y-1/2 w-20 h-20 rounded-full bg-[var(--accent-amber)]/10 border-2 border-[var(--accent-amber)] flex items-center justify-center">
                            <Sparkles className="text-[var(--accent-amber)]" size={32} />
                        </div>

                        {/* Thinkers in circle */}
                        {thinkers.map((thinker, index) => {
                            const pos = getThinkerPosition(index, thinkers.length);
                            const isSelected = selectedThinker === thinker.id;

                            return (
                                <button
                                    key={thinker.id}
                                    className={`thinker-item ${isSelected ? 'thinker-item-active' : ''}`}
                                    style={{
                                        left: `calc(50% + ${pos.x}px)`,
                                        top: `calc(50% + ${pos.y}px)`,
                                        transform: 'translate(-50%, -50%)',
                                    }}
                                    onClick={() => setThinker(thinker.id)}
                                    title={thinker.name}
                                >
                                    <span className="text-xs font-sans font-semibold text-center">
                                        {thinker.name.split(' ').pop()}
                                    </span>
                                </button>
                            );
                        })}
                    </div>
                </div>

                {/* Selected Thinker Info */}
                {selectedThinkerData && (
                    <div className="mb-6 p-4 bg-[var(--bg-secondary)] rounded-lg">
                        <h4 className="font-serif text-lg mb-2">{selectedThinkerData.name}</h4>
                        <p className="text-sm text-[var(--text-secondary)] mb-3">
                            {selectedThinkerData.description}
                        </p>
                        <div className="flex flex-wrap gap-2">
                            {selectedThinkerData.style_suggestions.map((style) => (
                                <button
                                    key={style}
                                    onClick={() => setStyle(style === selectedStyle ? null : style)}
                                    className={`px-3 py-1 rounded-full text-xs font-sans transition-colors ${selectedStyle === style
                                            ? 'bg-[var(--accent-amber)] text-white'
                                            : 'bg-[var(--sepia)] text-[var(--charcoal)] hover:bg-[var(--accent-amber)]/20'
                                        }`}
                                >
                                    {style}
                                </button>
                            ))}
                        </div>
                    </div>
                )}

                {/* Intent Selection */}
                <div className="mb-6">
                    <h3 className="text-sm font-sans text-[var(--text-secondary)] mb-3">
                        Select Intent
                    </h3>
                    <div className="grid grid-cols-2 gap-2">
                        {intents.map((intent) => (
                            <button
                                key={intent.id}
                                onClick={() => setIntent(intent.id)}
                                className={`p-3 rounded-lg text-left transition-all ${selectedIntent === intent.id
                                        ? 'bg-[var(--accent-amber)] text-white'
                                        : 'bg-[var(--bg-secondary)] hover:bg-[var(--sepia)]'
                                    }`}
                            >
                                <div className="font-sans font-medium text-sm mb-1 capitalize">
                                    {intent.id}
                                </div>
                                <div className="text-xs opacity-80">{intent.description}</div>
                            </button>
                        ))}
                    </div>
                </div>

                {/* Error Message */}
                {error && (
                    <div className="mb-4 p-3 bg-red-50 border border-red-200 rounded-lg text-red-800 text-sm">
                        {error}
                    </div>
                )}

                {/* Actions */}
                <div className="flex gap-3">
                    <button onClick={handleClose} className="btn btn-secondary flex-1">
                        Cancel
                    </button>
                    <button
                        onClick={handleTransform}
                        disabled={!selectedThinker || !selectedIntent || isTransforming}
                        className="btn btn-primary flex-1 flex items-center justify-center gap-2"
                    >
                        {isTransforming ? (
                            <>
                                <Loader2 size={16} className="animate-spin" />
                                Transforming...
                            </>
                        ) : (
                            <>
                                <Sparkles size={16} />
                                Transform
                            </>
                        )}
                    </button>
                </div>
            </div>
        </div>
    );
}
