/**
 * ThinkerDialog - Philosophical Transformation Interface
 * Allows selecting thinkers, intents, and output length for AI transformations
 */
'use client';

import { useState, useEffect } from 'react';
import { X, Sparkles, Loader2, Edit3, Check } from 'lucide-react';
import { useNoesisStore } from '@/lib/stores/noesis-store';
import { aiApi, type TransformRequest } from '@/lib/api/client';

interface Thinker {
    id: string;
    name: string;
    description: string;
    style_suggestions: string[];
    is_custom?: boolean;
}

interface Intent {
    id: string;
    description: string;
}

interface OutputLength {
    id: string;
    label: string;
    description: string;
    max_words: number;
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
    const [outputLengths, setOutputLengths] = useState<OutputLength[]>([]);
    const [selectedLength, setSelectedLength] = useState<string>('medium');
    const [isTransforming, setIsTransforming] = useState(false);
    const [error, setError] = useState<string | null>(null);

    // Custom thinker editing state
    const [editingCustom, setEditingCustom] = useState<string | null>(null);
    const [customPersona, setCustomPersona] = useState<string>('');
    const [customThinkers, setCustomThinkers] = useState<Record<string, { name: string; persona: string }>>({});

    // Load thinkers and intents
    useEffect(() => {
        if (isThinkerDialogOpen) {
            aiApi.getThinkers().then((data) => {
                setThinkers(data.thinkers || []);
                setIntents(data.intents || []);
                setOutputLengths(data.output_lengths || []);
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
                output_length: selectedLength,
                custom_persona: customThinkers[selectedThinker]?.persona || undefined,
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
                    output_length: selectedLength,
                },
                is_active: true,
                version_number: 0,
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
        setEditingCustom(null);
    };

    const handleSaveCustom = (thinkerId: string) => {
        setCustomThinkers({
            ...customThinkers,
            [thinkerId]: {
                name: customThinkers[thinkerId]?.name || `Custom ${thinkerId.split('_')[1]}`,
                persona: customPersona,
            },
        });
        setEditingCustom(null);
    };

    const selectedThinkerData = thinkers.find((t) => t.id === selectedThinker);

    // Separate core and custom thinkers
    const coreThinkers = thinkers.filter(t => !t.is_custom);
    const customSlots = thinkers.filter(t => t.is_custom);

    return (
        <div className="modal-overlay" onClick={handleClose}>
            <div
                className="modal-content max-h-[90vh] overflow-y-auto"
                onClick={(e) => e.stopPropagation()}
            >
                {/* Header */}
                <div className="flex items-center justify-between mb-6 sticky top-0 bg-[var(--bg-primary)] py-2 z-10">
                    <h2 className="text-2xl font-serif">Invoke Thinker Mode</h2>
                    <button
                        onClick={handleClose}
                        className="btn-ghost p-2"
                        aria-label="Close"
                    >
                        <X size={24} />
                    </button>
                </div>

                {/* Core Thinkers Grid */}
                <div className="mb-6">
                    <h3 className="text-sm font-sans text-[var(--text-secondary)] mb-3">
                        Select a Philosopher
                    </h3>
                    <div className="grid grid-cols-3 gap-2">
                        {coreThinkers.map((thinker) => {
                            const isSelected = selectedThinker === thinker.id;
                            return (
                                <button
                                    key={thinker.id}
                                    className={`p-3 rounded-lg text-left transition-all ${isSelected
                                            ? 'bg-[var(--accent-amber)] text-white'
                                            : 'bg-[var(--bg-secondary)] hover:bg-[var(--sepia)]'
                                        }`}
                                    onClick={() => setThinker(thinker.id)}
                                    title={thinker.description}
                                >
                                    <div className="font-sans font-medium text-sm truncate">
                                        {thinker.name}
                                    </div>
                                </button>
                            );
                        })}
                    </div>
                </div>

                {/* Custom Thinker Slots */}
                <div className="mb-6">
                    <h3 className="text-sm font-sans text-[var(--text-secondary)] mb-3">
                        Custom Thinkers (Click edit to customize)
                    </h3>
                    <div className="grid grid-cols-2 gap-2">
                        {customSlots.map((thinker) => {
                            const isSelected = selectedThinker === thinker.id;
                            const isEditing = editingCustom === thinker.id;
                            const customData = customThinkers[thinker.id];

                            return (
                                <div key={thinker.id} className="relative">
                                    {isEditing ? (
                                        <div className="p-3 bg-[var(--bg-secondary)] rounded-lg">
                                            <input
                                                type="text"
                                                placeholder="Custom persona description..."
                                                value={customPersona}
                                                onChange={(e) => setCustomPersona(e.target.value)}
                                                className="input input-sm w-full mb-2 text-sm"
                                            />
                                            <button
                                                onClick={() => handleSaveCustom(thinker.id)}
                                                className="btn btn-sm btn-primary w-full flex items-center justify-center gap-1"
                                            >
                                                <Check size={14} />
                                                Save
                                            </button>
                                        </div>
                                    ) : (
                                        <button
                                            className={`w-full p-3 rounded-lg text-left transition-all flex items-center justify-between ${isSelected
                                                    ? 'bg-[var(--accent-amber)] text-white'
                                                    : 'bg-[var(--bg-secondary)] hover:bg-[var(--sepia)]'
                                                }`}
                                            onClick={() => setThinker(thinker.id)}
                                        >
                                            <span className="font-sans font-medium text-sm">
                                                {customData?.name || thinker.name}
                                            </span>
                                            <Edit3
                                                size={14}
                                                className="opacity-50 hover:opacity-100"
                                                onClick={(e) => {
                                                    e.stopPropagation();
                                                    setEditingCustom(thinker.id);
                                                    setCustomPersona(customData?.persona || '');
                                                }}
                                            />
                                        </button>
                                    )}
                                </div>
                            );
                        })}
                    </div>
                </div>

                {/* Selected Thinker Info */}
                {selectedThinkerData && (
                    <div className="mb-6 p-4 bg-[var(--bg-secondary)] rounded-lg">
                        <h4 className="font-serif text-lg mb-2">{selectedThinkerData.name}</h4>
                        <p className="text-sm text-[var(--text-secondary)] mb-3">
                            {customThinkers[selectedThinkerData.id]?.persona || selectedThinkerData.description}
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

                {/* Output Length Selection */}
                <div className="mb-6">
                    <h3 className="text-sm font-sans text-[var(--text-secondary)] mb-3">
                        Output Length
                    </h3>
                    <div className="flex flex-wrap gap-2">
                        {outputLengths.map((length) => (
                            <button
                                key={length.id}
                                onClick={() => setSelectedLength(length.id)}
                                className={`px-4 py-2 rounded-lg text-sm font-sans transition-all ${selectedLength === length.id
                                        ? 'bg-[var(--accent-amber)] text-white'
                                        : 'bg-[var(--bg-secondary)] hover:bg-[var(--sepia)]'
                                    }`}
                                title={`${length.description} (~${length.max_words} words)`}
                            >
                                {length.label}
                            </button>
                        ))}
                    </div>
                    {selectedLength && outputLengths.find(l => l.id === selectedLength) && (
                        <p className="mt-2 text-xs text-[var(--text-muted)]">
                            {outputLengths.find(l => l.id === selectedLength)?.description}
                            {' '}(~{outputLengths.find(l => l.id === selectedLength)?.max_words} words)
                        </p>
                    )}
                </div>

                {/* Error Message */}
                {error && (
                    <div className="mb-4 p-3 bg-red-50 border border-red-200 rounded-lg text-red-800 text-sm">
                        {error}
                    </div>
                )}

                {/* Actions */}
                <div className="flex gap-3 sticky bottom-0 bg-[var(--bg-primary)] py-4">
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
