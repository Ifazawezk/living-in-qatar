import { createContentLoader } from 'vitepress'

export interface Topic {
  url: string
  slug: string
  lang: 'en' | 'ar'
  title: string
  description: string
  lastChecked: string
  sources: number
}

declare const data: Topic[]
export { data }

export default createContentLoader(['guide/*.md', 'ar/guide/*.md'], {
  includeSrc: true,
  transform(raw): Topic[] {
    return raw
      .filter((page) => !/\/guide\/(index)?$/.test(page.url))
      .map((page) => ({
        url: page.url,
        slug: page.url.split('/').pop() ?? '',
        lang: page.url.startsWith('/ar/') ? 'ar' : 'en',
        title: page.frontmatter.title,
        description: page.frontmatter.description,
        lastChecked: String(page.frontmatter.lastChecked ?? ''),
        sources: new Set([...(page.src ?? '').matchAll(/^\[\^([^\]\s]+)\]:/gm)].map((m) => m[1])).size
      }))
  }
})
