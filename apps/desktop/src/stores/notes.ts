import { defineStore } from "pinia";
import type { CreateNoteInput, Note } from "@pkos/shared";
import { createNote, listNotes } from "../api";

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
    }
  }
});
