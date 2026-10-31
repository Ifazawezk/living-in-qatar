<script setup lang="ts">
import { computed } from 'vue'
import { useData, withBase } from 'vitepress'
import { groups } from '../../groups'
import { data as topics } from '../topics.data'

const { lang } = useData()
const ar = computed(() => lang.value === 'ar')

const sections = computed(() => {
  const mine = topics.filter((t) => t.lang === (ar.value ? 'ar' : 'en'))
  return groups
    .map((group) => ({
      title: ar.value ? group.ar : group.en,
      items: group.slugs.map((slug) => mine.find((t) => t.slug === slug)).filter((t) => t !== undefined)
    }))
    .filter((group) => group.items.length > 0)
})
</script>

<template>
  <div class="topic-list">
    <section v-for="section in sections" :key="section.title" class="topic-group">
      <h2 class="topic-group-title">{{ section.title }}</h2>
      <div class="topic-grid">
        <a v-for="topic in section.items" :key="topic.url" class="topic-card" :href="withBase(topic.url)">
          <span class="topic-title">{{ topic.title }}</span>
          <span class="topic-desc">{{ topic.description }}</span>
          <span class="topic-meta">
            {{ ar ? 'عدد المصادر' : 'Sources' }}: {{ topic.sources }}
            <span aria-hidden="true">&middot;</span>
            {{ ar ? 'آخر تحقق' : 'Checked' }}: <span dir="ltr">{{ topic.lastChecked }}</span>
          </span>
        </a>
      </div>
    </section>
  </div>
</template>
