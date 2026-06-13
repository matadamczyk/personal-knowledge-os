<script setup lang="ts">
import { computed, onMounted, ref } from "vue";
import { useNotesStore } from "./stores/notes";

const notes = useNotesStore();
const title = ref("");
const content = ref("");

const canSave = computed(() => title.value.trim().length > 0 || content.value.trim().length > 0);

async function saveNote() {
  if (!canSave.value) return;

  await notes.create({
    title: title.value.trim() || "Untitled note",
    content: content.value.trim()
  });

  title.value = "";
  content.value = "";
}

onMounted(() => {
  notes.load();
});
</script>

<template>
  <main class="min-h-screen bg-stone-50 text-zinc-950">
    <section class="border-b border-zinc-200 bg-white">
      <div class="mx-auto flex max-w-6xl items-center justify-between px-6 py-4">
        <div>
          <h1 class="text-xl font-semibold">Personal Knowledge OS</h1>
          <p class="text-sm text-zinc-600">Notes first. Embeddings later.</p>
        </div>
        <div
          class="rounded border border-emerald-200 bg-emerald-50 px-3 py-1 text-sm text-emerald-800"
        >
          MVP
        </div>
      </div>
    </section>

    <section class="mx-auto grid max-w-6xl gap-6 px-6 py-6 lg:grid-cols-[380px_1fr]">
      <form class="space-y-4" @submit.prevent="saveNote">
        <div>
          <label class="mb-1 block text-sm font-medium text-zinc-700" for="note-title">Title</label>
          <input
            id="note-title"
            v-model="title"
            class="w-full rounded border border-zinc-300 bg-white px-3 py-2 outline-none focus:border-emerald-600"
            placeholder="Research idea"
          />
        </div>

        <div>
          <label class="mb-1 block text-sm font-medium text-zinc-700" for="note-content"
            >Note</label
          >
          <textarea
            id="note-content"
            v-model="content"
            class="min-h-48 w-full resize-y rounded border border-zinc-300 bg-white px-3 py-2 outline-none focus:border-emerald-600"
            placeholder="Capture a thought, source, or decision."
          />
        </div>

        <button
          class="w-full rounded bg-zinc-950 px-4 py-2 text-sm font-medium text-white disabled:cursor-not-allowed disabled:bg-zinc-300"
          type="submit"
          :disabled="!canSave"
        >
          Save note
        </button>
      </form>

      <div>
        <div class="mb-3 flex items-center justify-between">
          <h2 class="text-base font-semibold">Notes</h2>
          <span class="text-sm text-zinc-500">{{ notes.items.length }} total</span>
        </div>

        <div
          v-if="notes.error"
          class="rounded border border-red-200 bg-red-50 px-3 py-2 text-sm text-red-800"
        >
          {{ notes.error }}
        </div>

        <div
          v-else-if="notes.loading"
          class="rounded border border-zinc-200 bg-white px-3 py-2 text-sm text-zinc-600"
        >
          Loading notes...
        </div>

        <div v-else class="grid gap-3">
          <article
            v-for="note in notes.items"
            :key="note.id"
            class="rounded border border-zinc-200 bg-white p-4"
          >
            <h3 class="font-medium">{{ note.title }}</h3>
            <p class="mt-2 whitespace-pre-wrap text-sm leading-6 text-zinc-700">
              {{ note.content }}
            </p>
            <p class="mt-3 text-xs text-zinc-500">
              {{ new Date(note.createdAt).toLocaleString() }}
            </p>
          </article>

          <p
            v-if="notes.items.length === 0"
            class="rounded border border-zinc-200 bg-white px-3 py-8 text-center text-sm text-zinc-500"
          >
            No notes yet.
          </p>
        </div>
      </div>
    </section>
  </main>
</template>
