<script setup lang="ts">
import { computed, onMounted, ref, watch } from "vue";
import { useNotesStore } from "./stores/notes";
import { marked } from "marked";

const notes = useNotesStore();

// Local UI states
const searchQuery = ref("");
const selectedNoteId = ref<string | null>(null);
const currentTab = ref<"write" | "preview">("write");

// Input states
const editableTitle = ref("");
const editableContent = ref("");
const editableCategory = ref("");

// Saving status
const savingStatus = ref<"idle" | "saving" | "saved" | "error">("idle");
const savingStatusText = computed(() => {
  switch (savingStatus.value) {
    case "saving":
      return "Saving changes...";
    case "saved":
      return "Saved";
    case "error":
      return "Error saving";
    default:
      return "Synced";
  }
});

// Selected note reactive computed
const selectedNote = computed(() => {
  return notes.items.find((n) => n.id === selectedNoteId.value) || null;
});

// Sync store note to local editable fields when selectedNoteId changes
watch(selectedNoteId, (newId) => {
  const note = notes.items.find((n) => n.id === newId);
  if (note) {
    editableTitle.value = note.title;
    editableContent.value = note.content;
    editableCategory.value = note.category || "";
    savingStatus.value = "idle";
  } else {
    editableTitle.value = "";
    editableContent.value = "";
    editableCategory.value = "";
    savingStatus.value = "idle";
  }
});

// Filtered notes based on search query
const filteredNotes = computed(() => {
  const query = searchQuery.value.trim().toLowerCase();
  if (!query) return notes.items;
  return notes.items.filter((n) => {
    return (
      n.title.toLowerCase().includes(query) ||
      n.content.toLowerCase().includes(query) ||
      (n.category && n.category.toLowerCase().includes(query))
    );
  });
});

// Auto-save debouncing
let saveTimeout: ReturnType<typeof setTimeout> | null = null;

function onFieldInput() {
  savingStatus.value = "saving";
  if (saveTimeout) clearTimeout(saveTimeout);

  saveTimeout = setTimeout(async () => {
    if (!selectedNoteId.value) return;
    try {
      await notes.update(selectedNoteId.value, {
        title: editableTitle.value,
        content: editableContent.value,
        category: editableCategory.value || null
      });
      savingStatus.value = "saved";
    } catch (e) {
      console.error(e);
      savingStatus.value = "error";
    }
  }, 600); // 600ms debounce
}

// Select note helper
function selectNote(id: string) {
  // If there's a pending save, flush it immediately before changing notes
  if (savingStatus.value === "saving") {
    if (saveTimeout) {
      clearTimeout(saveTimeout);
      saveTimeout = null;
    }
    // Perform fast sync save
    notes
      .update(selectedNoteId.value!, {
        title: editableTitle.value,
        content: editableContent.value,
        category: editableCategory.value || null
      })
      .catch(console.error);
  }
  selectedNoteId.value = id;
}

// Create note helper
async function createNewNote() {
  try {
    const newNote = await notes.create({
      title: "Untitled Note",
      content: ""
    });
    selectedNoteId.value = newNote.id;
    currentTab.value = "write";
  } catch (e) {
    console.error("Failed to create note:", e);
  }
}

// Delete note helper
async function deleteActiveNote() {
  if (!selectedNoteId.value) return;
  const confirmDelete = confirm("Are you sure you want to delete this note?");
  if (!confirmDelete) return;

  const idToDelete = selectedNoteId.value;
  try {
    // Clear saveTimeout first to prevent saving a deleted note
    if (saveTimeout) {
      clearTimeout(saveTimeout);
      saveTimeout = null;
    }
    selectedNoteId.value = null;
    await notes.delete(idToDelete);
    // Auto-select another note if available
    if (notes.items.length > 0) {
      selectedNoteId.value = notes.items[0].id;
    }
  } catch (e) {
    console.error("Failed to delete note:", e);
  }
}

// Markdown Preview html parser
const previewHtml = computed(() => {
  try {
    return marked.parse(editableContent.value || "");
  } catch {
    return `<p class="text-red-500">Error parsing Markdown</p>`;
  }
});

// Date formatting helpers
function formatRelativeDate(dateStr: string) {
  try {
    const date = new Date(dateStr);
    const now = new Date();
    const diffMs = now.getTime() - date.getTime();
    const diffMins = Math.floor(diffMs / 60000);
    const diffHours = Math.floor(diffMins / 60);
    const diffDays = Math.floor(diffHours / 24);

    if (diffMins < 1) return "Just now";
    if (diffMins < 60) return `${diffMins}m ago`;
    if (diffHours < 24) return `${diffHours}h ago`;
    if (diffDays === 1) return "Yesterday";
    if (diffDays < 7) return `${diffDays}d ago`;

    return date.toLocaleDateString(undefined, { month: "short", day: "numeric" });
  } catch {
    return "";
  }
}

function formatFullDate(dateStr: string) {
  try {
    return new Date(dateStr).toLocaleString(undefined, {
      month: "short",
      day: "numeric",
      hour: "2-digit",
      minute: "2-digit"
    });
  } catch {
    return "";
  }
}

onMounted(async () => {
  await notes.load();
  if (notes.items.length > 0) {
    selectedNoteId.value = notes.items[0].id;
  }
});
</script>

<template>
  <div class="flex h-screen w-screen overflow-hidden bg-[#0f1013] text-[#f3f4f6]">
    <!-- Sidebar -->
    <aside class="flex w-80 flex-col border-r border-[#2a2e3b] bg-[#16181d]">
      <!-- Sidebar Header -->
      <div class="flex items-center justify-between border-b border-[#2a2e3b] px-5 py-4">
        <div>
          <h1 class="text-base font-semibold tracking-wide text-white">Personal Knowledge OS</h1>
          <p class="text-xs text-[#9ca3af]">Second Brain Workspace</p>
        </div>
        <span
          class="rounded border border-[#2a2e3b] bg-[#1e2129] px-2 py-0.5 text-[10px] font-medium tracking-wider text-[#10b981] uppercase"
        >
          MVP
        </span>
      </div>

      <!-- Search Box -->
      <div class="p-4">
        <div class="relative flex items-center">
          <svg
            class="absolute left-3 h-4 w-4 text-[#9ca3af]"
            fill="none"
            stroke="currentColor"
            viewBox="0 0 24 24"
          >
            <path
              stroke-linecap="round"
              stroke-linejoin="round"
              stroke-width="2"
              d="M21 21l-6-6m2-5a7 7 0 11-14 0 7 7 0 0114 0z"
            />
          </svg>
          <input
            v-model="searchQuery"
            placeholder="Search notes..."
            class="w-full rounded-md border border-[#2a2e3b] bg-[#0f1013] py-1.5 pr-4 pl-9 text-sm text-[#f3f4f6] placeholder-[#9ca3af] outline-none transition focus:border-[#10b981]"
          />
        </div>
      </div>

      <!-- Notes List -->
      <div class="flex-1 overflow-y-auto px-2 pb-4 space-y-1">
        <div
          v-for="note in filteredNotes"
          :key="note.id"
          :class="[
            'group relative flex flex-col rounded-md p-3 cursor-pointer transition select-none',
            selectedNoteId === note.id
              ? 'bg-[#202225] border-l-2 border-[#10b981] pl-[10px]'
              : 'hover:bg-[#1e2129] text-[#9ca3af] hover:text-[#f3f4f6]'
          ]"
          @click="selectNote(note.id)"
        >
          <div class="flex items-start justify-between">
            <h3
              :class="[
                'font-medium text-sm truncate pr-2',
                selectedNoteId === note.id ? 'text-white' : 'text-[#f3f4f6]'
              ]"
            >
              {{ note.title || "Untitled Note" }}
            </h3>
            <span
              v-if="note.category"
              class="shrink-0 rounded bg-[#2a2e3b] px-1.5 py-0.5 text-[10px] font-medium text-[#10b981]"
            >
              {{ note.category }}
            </span>
          </div>
          <p class="mt-1 text-xs leading-relaxed text-[#9ca3af] line-clamp-2">
            {{ note.content || "Empty note..." }}
          </p>
          <span class="mt-2 text-[10px] text-[#9ca3af]/60">
            {{ formatRelativeDate(note.updatedAt) }}
          </span>
        </div>

        <div
          v-if="filteredNotes.length === 0"
          class="flex flex-col items-center justify-center py-12 text-center"
        >
          <p class="text-xs text-[#9ca3af]">No notes found.</p>
        </div>
      </div>

      <!-- Sidebar Footer -->
      <div class="border-t border-[#2a2e3b] p-4">
        <button
          class="flex w-full items-center justify-center gap-2 rounded-md bg-[#10b981] px-4 py-2 text-sm font-medium text-white shadow-md shadow-[#10b981]/10 transition hover:bg-[#059669] active:scale-95"
          @click="createNewNote"
        >
          <svg class="h-4 w-4" fill="none" stroke="currentColor" viewBox="0 0 24 24">
            <path
              stroke-linecap="round"
              stroke-linejoin="round"
              stroke-width="2"
              d="M12 4v16m8-8H4"
            />
          </svg>
          Create Note
        </button>
      </div>
    </aside>

    <!-- Main Workspace -->
    <main class="flex flex-1 flex-col overflow-hidden bg-[#0f1013]">
      <!-- Editor Workspace -->
      <div v-if="selectedNote" class="flex flex-1 flex-col overflow-hidden">
        <!-- Workspace Header -->
        <div
          class="flex items-center justify-between border-b border-[#2a2e3b] bg-[#16181d] px-6 py-3"
        >
          <!-- Tabs & Status -->
          <div class="flex items-center gap-4">
            <div class="flex rounded-md border border-[#2a2e3b] bg-[#0f1013] p-1">
              <button
                :class="[
                  'rounded px-3 py-1 text-xs font-medium transition select-none',
                  currentTab === 'write'
                    ? 'bg-[#1e2129] text-white shadow-sm'
                    : 'text-[#9ca3af] hover:text-white'
                ]"
                @click="currentTab = 'write'"
              >
                Write
              </button>
              <button
                :class="[
                  'rounded px-3 py-1 text-xs font-medium transition select-none',
                  currentTab === 'preview'
                    ? 'bg-[#1e2129] text-white shadow-sm'
                    : 'text-[#9ca3af] hover:text-white'
                ]"
                @click="currentTab = 'preview'"
              >
                Preview
              </button>
            </div>

            <!-- Auto-save Status Indicator -->
            <span class="flex items-center gap-1.5 text-xs text-[#9ca3af]">
              <span v-if="savingStatus === 'saving'" class="relative flex h-2 w-2">
                <span
                  class="absolute inline-flex h-full w-full animate-ping rounded-full bg-[#10b981] opacity-75"
                ></span>
                <span class="relative inline-flex h-2 w-2 rounded-full bg-[#10b981]"></span>
              </span>
              <span
                v-else-if="savingStatus === 'saved'"
                class="flex items-center gap-0.5 text-[#10b981]"
              >
                <svg class="h-3 w-3" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                  <path
                    stroke-linecap="round"
                    stroke-linejoin="round"
                    stroke-width="3"
                    d="M5 13l4 4L19 7"
                  />
                </svg>
              </span>
              <span v-else class="h-2 w-2 rounded-full bg-zinc-600"></span>
              {{ savingStatusText }}
            </span>
          </div>

          <!-- Actions -->
          <div class="flex items-center gap-2">
            <button
              class="rounded-md border border-[#2a2e3b] bg-[#16181d] p-2 text-[#9ca3af] transition hover:border-[#f87171]/50 hover:bg-[#7f1d1d]/20 hover:text-[#f87171]"
              title="Delete Note"
              @click="deleteActiveNote"
            >
              <svg class="h-4 w-4" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                <path
                  stroke-linecap="round"
                  stroke-linejoin="round"
                  stroke-width="2"
                  d="M19 7l-.867 12.142A2 2 0 0116.138 21H7.862a2 2 0 01-1.995-1.858L5 7m5 4v6m4-6v6m1-10V4a1 1 0 00-1-1h-4a1 1 0 00-1 1v3M4 7h16"
                />
              </svg>
            </button>
          </div>
        </div>

        <!-- Editor Title & Metadata -->
        <div class="flex flex-col gap-3 border-b border-[#2a2e3b] px-8 py-5">
          <input
            v-model="editableTitle"
            placeholder="Untitled Note"
            class="w-full bg-transparent text-2xl font-bold tracking-tight text-white outline-none placeholder-[#9ca3af]/40"
            @input="onFieldInput"
          />

          <div class="flex items-center gap-4 text-xs text-[#9ca3af]">
            <div class="flex items-center gap-1.5">
              <span class="font-medium text-[#9ca3af]/80">Category:</span>
              <input
                v-model="editableCategory"
                placeholder="Uncategorized"
                class="rounded border border-[#2a2e3b] bg-[#16181d] px-2 py-0.5 text-xs text-white outline-none focus:border-[#10b981]"
                @input="onFieldInput"
              />
            </div>
            <div class="h-4 w-px bg-[#2a2e3b]"></div>
            <div>Last updated: {{ formatFullDate(selectedNote.updatedAt) }}</div>
          </div>
        </div>

        <!-- Textarea / Preview Container -->
        <div class="flex-1 overflow-hidden">
          <!-- Write Tab -->
          <div v-show="currentTab === 'write'" class="h-full w-full p-8">
            <textarea
              v-model="editableContent"
              placeholder="Start writing in Markdown..."
              class="h-full w-full resize-none bg-transparent font-mono text-sm leading-relaxed text-[#e5e7eb] outline-none placeholder-[#9ca3af]/30"
              @input="onFieldInput"
            />
          </div>

          <!-- Preview Tab -->
          <div v-show="currentTab === 'preview'" class="h-full w-full overflow-y-auto px-8 py-6">
            <!-- eslint-disable-next-line vue/no-v-html -->
            <div class="markdown-preview" v-html="previewHtml"></div>
          </div>
        </div>
      </div>

      <!-- Empty State -->
      <div v-else class="flex flex-1 flex-col items-center justify-center p-12 text-center">
        <div class="rounded-full border border-[#2a2e3b] bg-[#16181d] p-4 text-[#10b981] shadow-lg">
          <svg class="h-8 w-8 animate-pulse" fill="none" stroke="currentColor" viewBox="0 0 24 24">
            <path
              stroke-linecap="round"
              stroke-linejoin="round"
              stroke-width="2"
              d="M9.663 17h4.673M12 3v1m6.364 1.636l-.707.707M21 12h-1M4 12H3m3.343-5.657l-.707-.707m2.828 9.9a5 5 0 117.072 0l-.548.547A3.374 3.374 0 0014 18.469V19a2 2 0 11-4 0v-.531c0-.895-.356-1.754-.988-2.386l-.548-.547z"
            />
          </svg>
        </div>
        <h2 class="mt-4 text-base font-semibold text-white">Your Second Brain</h2>
        <p class="mt-1 max-w-xs text-xs leading-relaxed text-[#9ca3af]">
          Create a new note or select an existing one to begin capture. Supports rich Markdown
          formatting.
        </p>
      </div>
    </main>
  </div>
</template>
