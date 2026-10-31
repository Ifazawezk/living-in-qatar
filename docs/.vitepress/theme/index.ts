import { h } from 'vue'
import type { Theme } from 'vitepress'
import DefaultTheme from 'vitepress/theme'
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
