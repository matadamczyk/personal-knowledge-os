export interface Note {
  id: string;
  title: string;
  content: string;
  summary?: string | null;
  category?: string | null;
  categoryConfidence?: number | null;
  createdAt: string;
  updatedAt: string;
}

export interface CreateNoteInput {
  title: string;
  content: string;
}

export interface UpdateNoteInput {
  title?: string;
  content?: string;
  summary?: string | null;
  category?: string | null;
}

export interface SearchResult {
  id: string;
  score: number;
  title: string;
  excerpt: string;
}
