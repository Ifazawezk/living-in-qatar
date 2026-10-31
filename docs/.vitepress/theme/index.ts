import { h } from 'vue'
import type { Theme } from 'vitepress'
import DefaultTheme from 'vitepress/theme'
import '@fontsource/ibm-plex-sans-arabic/400.css'
import '@fontsource/ibm-plex-sans-arabic/600.css'
import '@fontsource/ibm-plex-sans-arabic/700.css'
import './custom.css'
import PageMeta from './components/PageMeta.vue'
import TopicList from './components/TopicList.vue'

export default {
  extends: DefaultTheme,
  Layout() {
    return h(DefaultTheme.Layout, null, {
      'doc-before': () => h(PageMeta)
    })
  },
  enhanceApp({ app }) {
    app.component('TopicList', TopicList)
  }
} satisfies Theme
