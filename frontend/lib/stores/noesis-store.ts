/**
 * Noesis Store - Global state management with Zustand
 * Manages documents, blocks, active selections, and UI state
 */
import { create } from 'zustand';

// Types
export interface BlockVersion {
    id: string;
    block_id: string;
    content: string;
    author_type: string;
    transform_intent?: string;
    transform_params?: Record<string, any>;
    is_active: boolean;
    version_number: number;
    created_at: string;
}

export interface Block {
    id: string;
    document_id: string;
    position_index: number;
    block_type: 'paragraph' | 'header' | 'quote' | 'axiom' | 'list';
    created_at: string;
    updated_at: string;
    active_version?: BlockVersion;
    version_count?: number;
}

export interface Document {
    id: string;
    title: string;
    owner_id: string;
    tags: string[];
    folder_path: string;
    created_at: string;
    updated_at: string;
    blocks?: Block[];
    block_count?: number;
}

export interface Thinker {
    id: string;
    name: string;
    description: string;
    style_suggestions: string[];
}

interface NoesisStore {
    // Current state
    currentDocument: Document | null;
    documents: Document[];
    selectedBlockId: string | null;
    selectedVersionId: string | null;

    // UI state
    isThinkerDialogOpen: boolean;
    isVersionHistoryOpen: boolean;
    isSidebarOpen: boolean;

    // Thinker Mode state
    selectedThinker: string | null;
    selectedIntent: string | null;
    selectedStyle: string | null;

    // Actions - Documents
    setCurrentDocument: (doc: Document | null) => void;
    setDocuments: (docs: Document[]) => void;
    addDocument: (doc: Document) => void;
    updateDocument: (id: string, updates: Partial<Document>) => void;

    // Actions - Blocks
    setSelectedBlock: (blockId: string | null) => void;
    addBlock: (block: Block) => void;
    updateBlock: (blockId: string, updates: Partial<Block>) => void;
    removeBlock: (blockId: string) => void;
    reorderBlocks: (fromIndex: number, toIndex: number) => void;

    // Actions - Versions
    setSelectedVersion: (versionId: string | null) => void;
    addVersion: (blockId: string, version: BlockVersion) => void;
    activateVersion: (blockId: string, versionId: string) => void;

    // Actions - UI
    openThinkerDialog: () => void;
    closeThinkerDialog: () => void;
    toggleVersionHistory: () => void;
    toggleSidebar: () => void;

    // Actions - Thinker Mode
    setThinker: (thinkerId: string | null) => void;
    setIntent: (intent: string | null) => void;
    setStyle: (style: string | null) => void;
    resetThinkerSelection: () => void;
}

export const useNoesisStore = create<NoesisStore>((set, get) => ({
    // Initial state
    currentDocument: null,
    documents: [],
    selectedBlockId: null,
    selectedVersionId: null,

    isThinkerDialogOpen: false,
    isVersionHistoryOpen: false,
    isSidebarOpen: true,

    selectedThinker: null,
    selectedIntent: null,
    selectedStyle: null,

    // Document actions
    setCurrentDocument: (doc) => set({ currentDocument: doc }),

    setDocuments: (docs) => set({ documents: docs }),

    addDocument: (doc) => set((state) => ({
        documents: [...state.documents, doc],
    })),

    updateDocument: (id, updates) => set((state) => ({
        documents: state.documents.map((doc) =>
            doc.id === id ? { ...doc, ...updates } : doc
        ),
        currentDocument:
            state.currentDocument?.id === id
                ? { ...state.currentDocument, ...updates }
                : state.currentDocument,
    })),

    // Block actions
    setSelectedBlock: (blockId) => set({ selectedBlockId: blockId }),

    addBlock: (block) => set((state) => {
        if (!state.currentDocument) return state;

        const updatedBlocks = [...(state.currentDocument.blocks || []), block];
        return {
            currentDocument: {
                ...state.currentDocument,
                blocks: updatedBlocks,
            },
        };
    }),

    updateBlock: (blockId, updates) => set((state) => {
        if (!state.currentDocument?.blocks) return state;

        return {
            currentDocument: {
                ...state.currentDocument,
                blocks: state.currentDocument.blocks.map((block) =>
                    block.id === blockId ? { ...block, ...updates } : block
                ),
            },
        };
    }),

    removeBlock: (blockId) => set((state) => {
        if (!state.currentDocument?.blocks) return state;

        return {
            currentDocument: {
                ...state.currentDocument,
                blocks: state.currentDocument.blocks.filter((b) => b.id !== blockId),
            },
        };
    }),

    reorderBlocks: (fromIndex, toIndex) => set((state) => {
        if (!state.currentDocument?.blocks) return state;

        const blocks = [...state.currentDocument.blocks];
        const [removed] = blocks.splice(fromIndex, 1);
        blocks.splice(toIndex, 0, removed);

        // Update position_index for all blocks
        const reindexed = blocks.map((block, index) => ({
            ...block,
            position_index: index,
        }));

        return {
            currentDocument: {
                ...state.currentDocument,
                blocks: reindexed,
            },
        };
    }),

    // Version actions
    setSelectedVersion: (versionId) => set({ selectedVersionId: versionId }),

    addVersion: (blockId, version) => set((state) => {
        if (!state.currentDocument?.blocks) return state;

        return {
            currentDocument: {
                ...state.currentDocument,
                blocks: state.currentDocument.blocks.map((block) => {
                    if (block.id !== blockId) return block;

                    return {
                        ...block,
                        active_version: version.is_active ? version : block.active_version,
                        version_count: (block.version_count || 0) + 1,
                    };
                }),
            },
        };
    }),

    activateVersion: (blockId, versionId) => set((state) => {
        // This would typically trigger an API call
        // For now, just update the UI state
        return { selectedVersionId: versionId };
    }),

    // UI actions
    openThinkerDialog: () => set({ isThinkerDialogOpen: true }),
    closeThinkerDialog: () => set({ isThinkerDialogOpen: false }),
    toggleVersionHistory: () => set((state) => ({
        isVersionHistoryOpen: !state.isVersionHistoryOpen,
    })),
    toggleSidebar: () => set((state) => ({
        isSidebarOpen: !state.isSidebarOpen,
    })),

    // Thinker Mode actions
    setThinker: (thinkerId) => set({ selectedThinker: thinkerId }),
    setIntent: (intent) => set({ selectedIntent: intent }),
    setStyle: (style) => set({ selectedStyle: style }),
    resetThinkerSelection: () => set({
        selectedThinker: null,
        selectedIntent: null,
        selectedStyle: null,
    }),
}));
