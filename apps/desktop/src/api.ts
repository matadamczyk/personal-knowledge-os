import axios from "axios";
import type { CreateNoteInput, Note, UpdateNoteInput } from "@pkos/shared";

const api = axios.create({
  baseURL: import.meta.env.VITE_API_URL ?? "http://127.0.0.1:8000"
});

export async function listNotes(): Promise<Note[]> {
  const response = await api.get<Note[]>("/api/notes");
  return response.data;
}

export async function createNote(input: CreateNoteInput): Promise<Note> {
  const response = await api.post<Note>("/api/notes", input);
  return response.data;
}

export async function updateNote(id: string, input: UpdateNoteInput): Promise<Note> {
  const response = await api.put<Note>(`/api/notes/${id}`, input);
  return response.data;
}

export async function deleteNote(id: string): Promise<void> {
  await api.delete(`/api/notes/${id}`);
}

export async function healthCheck(): Promise<{ status: string }> {
  const response = await api.get<{ status: string }>("/health");
  return response.data;
}
