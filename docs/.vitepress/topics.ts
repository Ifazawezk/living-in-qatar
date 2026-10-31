import fs from 'node:fs'
import path from 'node:path'
import { fileURLToPath } from 'node:url'
import type { DefaultTheme } from 'vitepress'
import { groups } from './groups'

const docs = path.resolve(path.dirname(fileURLToPath(import.meta.url)), '..')

type Locale = 'en' | 'ar'

export { groups }

function guideDir(locale: Locale) {
  return locale === 'en' ? path.join(docs, 'guide') : path.join(docs, 'ar', 'guide')
}

export function pageTitle(file: string): string | undefined {
  const text = fs.readFileSync(file, 'utf8')
  const match = text.match(/^---\r?\n[\s\S]*?^title:\s*(.+?)\s*$/m)
  return match?.[1].replace(/^['"]|['"]$/g, '')
}

export function topicSlugs(locale: Locale = 'en'): string[] {
  return groups
    .flatMap((group) => group.slugs)
    .filter((slug) => fs.existsSync(path.join(guideDir(locale), `${slug}.md`)))
}

export function sidebar(locale: Locale): DefaultTheme.SidebarItem[] {
  const prefix = locale === 'en' ? '' : '/ar'
  return groups
    .map((group) => ({
      text: group[locale],
      items: group.slugs
        .map((slug) => path.join(guideDir(locale), `${slug}.md`))
        .filter((file) => fs.existsSync(file))
        .map((file) => ({
          text: pageTitle(file) ?? path.basename(file, '.md'),
          link: `${prefix}/guide/${path.basename(file, '.md')}`
        }))
    }))
    .filter((group) => group.items.length > 0)
}

// Counts the footnote definitions in a page, so the page header can say how
// many official sources back it up.
export function sourceCount(file: string): number {
  if (!fs.existsSync(file)) return 0
  const text = fs.readFileSync(file, 'utf8')
  return new Set([...text.matchAll(/^\[\^([^\]\s]+)\]:/gm)].map((m) => m[1])).size
}
