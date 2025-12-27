/**
 * Editor Page - Dynamic route for editing documents
 */
'use client';

import { DocumentEditor } from '@/components/editor/DocumentEditor';

export default function EditorPage({ params }: { params: { id: string } }) {
    return <DocumentEditor documentId={params.id} />;
}
