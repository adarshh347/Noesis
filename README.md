# Noesis: The Creative Philosophy Studio

A digital workspace designed for rigorous intellectual creation. Unlike standard note-taking apps that treat text as static data, Noesis treats writing as a dynamic, iterative thinking process.

## Core Philosophy

**Writing as Thinking**: Every paragraph is a malleable object with infinite versions.

**The Dialectic Engine**: AI is not a copywriter; it is a sparring partner (Thinker Mode).

**Philosophical Rigor**: Built-in logic checking, fallacy detection, and structural analysis.

## Key Features

### 🧩 Block-Based Editor (The Loom)
- Modular, version-controlled writing
- Drag-and-drop paragraph reordering
- Vertical version stacking (never delete, only evolve)
- Visual diff between versions

### 🎭 Thinker Mode (The Dialectic)
- Transform blocks through the lens of history's greatest thinkers
- Style transfer: Nietzsche, Kant, Wittgenstein, Sankara, and more
- A/B comparison between original and transformed versions
- Customizable intent: critique, steel-man, simplify, mystify

### 🔍 Philosophical Intelligence (The Oracle)
- Real-time logic linting
- Fallacy detection (Ad Hominem, Straw Man, Circular Reasoning)
- Hidden assumption highlighting
- Structural argument mapping

### 📚 The Workspace (The Library)
- Hierarchical folders + graph view
- Semantic search across your knowledge base
- Tag-based organization
- "Idea Sidebar" for unused blocks and references

## Tech Stack

- **Frontend**: Next.js 14+ (App Router) with TypeScript
- **Backend**: FastAPI (Python)
- **Database**: PostgreSQL + pgvector for semantic search
- **AI**: Groq LLMs (easily swappable)
- **Editor**: TipTap (ProseMirror wrapper)
- **UI**: Radix UI + Tailwind CSS
- **State**: Zustand

## Design Aesthetic: "Digital Monastery"

- **Typography**: Crimson Pro / EB Garamond (serif) + Inter (sans-serif)
- **Colors**: Paper-white, sepia, charcoal, deep slate
- **Whitespace**: Aggressive use to let thoughts breathe
- **Interactions**: Slow, deliberate animations
- **Interface**: Receding UI - controls appear only when needed

## Project Structure

```
Noesis/
├── backend/          # FastAPI application
│   ├── models/       # SQLAlchemy models
│   ├── routes/       # API endpoints
│   ├── services/     # Business logic & LLM service
│   └── main.py
├── frontend/         # Next.js application
│   ├── app/          # App router pages
│   ├── components/   # React components
│   ├── lib/          # Utilities & stores
│   └── types/        # TypeScript types
└── README.md
```

## Getting Started

See `SETUP.md` for detailed installation and development instructions.

## Development Roadmap

- [x] Phase 0: Project initialization
- [ ] Phase 1: Foundation (Workspace, Editor, Auth)
- [ ] Phase 2: Thinker Engine (AI transformations)
- [ ] Phase 3: Intelligence Layer (Logic linting, semantic search)
- [ ] Phase 4: Polish & Aesthetics

Blocks are containers, not content - they hold a position and type
Versions hold the actual text - content never overwrites, only stacks
Every AI transformation creates a new version - preserving intellectual history
is_active controls visibility - easy to time-travel between versions
Cascade deletes ensure referential integrity - delete a document, all blocks and versions go with it
