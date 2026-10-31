<script setup lang="ts">
import { computed, onMounted, onBeforeUnmount, ref } from 'vue'
import { useData } from 'vitepress'

const { lang, page } = useData()
const ar = computed(() => lang.value === 'ar')
const done = ref(0)
const total = ref(0)

// Ticks are kept in this browser only. Nothing is sent anywhere.
const key = computed(() => `living-in-qatar:checklist:${page.value.relativePath}`)

function boxes(): HTMLInputElement[] {
  return Array.from(document.querySelectorAll<HTMLInputElement>('.vp-doc input.task-box'))
}

function load(): Record<string, boolean> {
  try {
    return JSON.parse(localStorage.getItem(key.value) ?? '{}')
  } catch {
    return {}
  }
}

function save() {
  const state: Record<string, boolean> = {}
  for (const box of boxes()) state[box.dataset.task ?? box.id] = box.checked
  try {
    localStorage.setItem(key.value, JSON.stringify(state))
  } catch {
    // private mode or storage disabled: ticks just won't be remembered
  }
  count()
}

function count() {
  const all = boxes()
  total.value = all.length
  done.value = all.filter((box) => box.checked).length
}

function clearAll() {
  for (const box of boxes()) box.checked = false
  save()
}

function print() {
  window.print()
}

function onChange(event: Event) {
  if ((event.target as HTMLElement).classList?.contains('task-box')) save()
}

onMounted(() => {
  const state = load()
  for (const box of boxes()) {
    const id = box.dataset.task ?? box.id
    if (id in state) box.checked = state[id]
  }
  count()
  document.addEventListener('change', onChange)
})

onBeforeUnmount(() => document.removeEventListener('change', onChange))
</script>

<template>
  <div class="checklist-tools">
    <button type="button" class="checklist-button primary" @click="print">
      {{ ar ? 'اطبع القائمة' : 'Print this checklist' }}
    </button>
    <button type="button" class="checklist-button" @click="clearAll">
      {{ ar ? 'امسح العلامات' : 'Clear all ticks' }}
    </button>
    <span class="checklist-progress" aria-live="polite">
      {{ ar ? `أنجزت ${done} من ${total}` : `${done} of ${total} done` }}
    </span>
  </div>
</template>
