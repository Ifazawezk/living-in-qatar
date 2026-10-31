import path from 'node:path'
import { defineConfig } from 'vitepress'
import footnote from 'markdown-it-footnote'
import { sidebar, sourceCount } from './topics'

const repo = 'https://github.com/Ifazawezk/living-in-qatar'
const site = 'https://ifazawezk.github.io/living-in-qatar/'

export default defineConfig({
  base: '/living-in-qatar/',
  cleanUrls: true,
  lastUpdated: false,
  sitemap: { hostname: site },

  head: [
    ['link', { rel: 'icon', type: 'image/svg+xml', href: '/living-in-qatar/favicon.svg' }],
    ['meta', { name: 'theme-color', content: '#8a1538' }],
    ['meta', { property: 'og:type', content: 'website' }],
  ],

  markdown: {
    config(md) {
      md.use(footnote)
      // Show [1] every time a source is cited, not [1:2], [1:3] and so on
      md.renderer.rules.footnote_caption = (tokens, idx) => `[${tokens[idx].meta.id + 1}]`
      // A plain arrow instead of the default emoji-style back link
      md.renderer.rules.footnote_anchor = (tokens, idx, _options, env, slf) => {
        let id = slf.rules.footnote_anchor_name!(tokens, idx, _options, env, slf)
        if (tokens[idx].meta.subId > 0) id += `:${tokens[idx].meta.subId}`
        return ` <a href="#fnref${id}" class="footnote-backref" aria-label="Back to text">&#8593;</a>`
      }
    }
  },

  transformPageData(pageData, { siteConfig }) {
    if (/(^|\/)guide\/(?!index)/.test(pageData.relativePath)) {
      pageData.frontmatter.sourceCount = sourceCount(path.join(siteConfig.srcDir, pageData.relativePath))
    }
  },

  locales: {
    root: {
      label: 'English',
      lang: 'en',
      title: 'Living in Qatar',
      description:
        'A practical guide to living in Qatar. Every claim links to the official source, in English and Arabic.',
      themeConfig: {
        nav: [
          { text: 'Guide', link: '/guide/', activeMatch: '^/guide/' },
        ],
        sidebar: {
          '/guide/': [{ text: 'All topics', link: '/guide/' }, ...sidebar('en')]
        },
        editLink: {
          pattern: `${repo}/edit/main/docs/:path`,
          text: 'Suggest a correction on GitHub'
        },
        outline: { level: [2, 3], label: 'On this page' },
        footer: {
          message:
            'Not legal advice. Always confirm on the official page linked in the sources. Content CC BY 4.0, code MIT.',
          copyright: 'Copyright 2026 Mohaned Elhagar and contributors'
        }
      }
    }
  },

  themeConfig: {
    logo: { src: '/favicon.svg', alt: '' },
    socialLinks: [{ icon: 'github', link: repo }]
  }
})
