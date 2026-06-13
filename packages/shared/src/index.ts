export interface Note {
  id: string;
  title: string;
  content: string;
  createdAt: string;
  updatedAt: string;
}

export interface CreateNoteInput {
  title: string;
  content: string;
}

export interface SearchResult {
  id: string;
  score: number;
  title: string;
  excerpt: string;
}
