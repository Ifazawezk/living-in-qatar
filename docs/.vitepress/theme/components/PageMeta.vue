<script setup lang="ts">
import { computed } from 'vue'
import { useData } from 'vitepress'

const { frontmatter, lang, page } = useData()

const ar = computed(() => lang.value === 'ar')
const show = computed(() => Boolean(frontmatter.value.lastChecked))

const issueUrl = computed(() => {
  const title = `Correction: ${page.value.title}`
  const body = [
    `Page: docs/${page.value.relativePath}`,
    '',
    'What is wrong or out of date:',
    '',
    'Link to the official page that shows the correct information:',
    ''
  ].join('\n')
  return (
    'https://github.com/Ifazawezk/living-in-qatar/issues/new' +
    `?title=${encodeURIComponent(title)}&body=${encodeURIComponent(body)}`
  )
})
</script>

<template>
  <aside v-if="show" class="page-meta" :aria-label="ar ? 'عن هذه الصفحة' : 'About this page'">
    <p class="page-meta-facts">
      <span class="pill">
        {{ ar ? 'آخر تحقق' : 'Last checked' }}: <strong dir="ltr">{{ frontmatter.lastChecked }}</strong>
      </span>
      <span v-if="frontmatter.sourceCount" class="pill">
        {{ ar ? 'عدد المصادر الرسمية' : 'Official sources' }}: <strong>{{ frontmatter.sourceCount }}</strong>
      </span>
    </p>
    <p v-if="ar" class="page-meta-note">
      كل معلومة هنا مربوطة بصفحة رسمية. الأنظمة والرسوم تتغير، فراجع المصدر قبل أن تتخذ أي خطوة. هذا الدليل ليس
      استشارة قانونية.
      <a :href="issueUrl" target="_blank" rel="noopener">أبلغ عن معلومة قديمة</a>
    </p>
    <p v-else class="page-meta-note">
      Every fact here links to an official page. Rules and fees change, so open the source before you act. This is
      not legal advice.
      <a :href="issueUrl" target="_blank" rel="noopener">Report something out of date</a>
    </p>
  </aside>
</template>
