import { defineStore } from "pinia";
import type { CreateNoteInput, Note, UpdateNoteInput } from "@pkos/shared";
import { createNote, listNotes, updateNote, deleteNote } from "../api";

interface NotesState {
  items: Note[];
  loading: boolean;
  error: string | null;
}

export const useNotesStore = defineStore("notes", {
  state: (): NotesState => ({
    items: [],
    loading: false,
    error: null
  }),
  actions: {
    async load() {
      this.loading = true;
      this.error = null;
      try {
        this.items = await listNotes();
      } catch (error) {
        this.error = error instanceof Error ? error.message : "Failed to load notes";
      } finally {
        this.loading = false;
      }
    },
    async create(input: CreateNoteInput) {
      const note = await createNote(input);
      this.items.unshift(note);
      return note;
    },
    async update(id: string, input: UpdateNoteInput) {
      const updated = await updateNote(id, input);
      const index = this.items.findIndex((item) => item.id === id);
      if (index !== -1) {
        this.items[index] = updated;
      }
      return updated;
    },
    async delete(id: string) {
      await deleteNote(id);
      this.items = this.items.filter((item) => item.id !== id);
    }
  }
});
