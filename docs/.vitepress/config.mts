import path from 'node:path'
import { defineConfig, type DefaultTheme } from 'vitepress'
import footnote from 'markdown-it-footnote'
import { sidebar, sourceCount } from './topics'
import { taskLists } from './task-lists'
import { normalizeTerm } from './normalize.mjs'

const repo = 'https://github.com/Ifazawezk/living-in-qatar'
const site = 'https://ifazawezk.github.io/living-in-qatar/'

const searchTranslations: DefaultTheme.LocalSearchOptions['translations'] = {
  button: { buttonText: 'بحث', buttonAriaLabel: 'بحث' },
  modal: {
    displayDetails: 'عرض التفاصيل',
    resetButtonTitle: 'مسح البحث',
    backButtonTitle: 'إغلاق البحث',
    noResultsText: 'لا توجد نتائج عن',
    footer: {
      selectText: 'فتح',
      selectKeyAriaLabel: 'إدخال',
      navigateText: 'تنقل',
      navigateUpKeyAriaLabel: 'سهم لأعلى',
      navigateDownKeyAriaLabel: 'سهم لأسفل',
      closeText: 'إغلاق',
      closeKeyAriaLabel: 'هروب'
    }
  }
}

export default defineConfig({
  base: '/living-in-qatar/',
  cleanUrls: true,
  lastUpdated: false,
  sitemap: { hostname: site },

  head: [
    ['link', { rel: 'icon', type: 'image/svg+xml', href: '/living-in-qatar/favicon.svg' }],
    ['meta', { name: 'theme-color', content: '#8a1538' }],
    ['meta', { property: 'og:type', content: 'website' }],
    ['meta', { property: 'og:image', content: `${site}og.png` }],
    ['meta', { name: 'twitter:card', content: 'summary_large_image' }]
  ],

  markdown: {
    config(md) {
      md.use(footnote)
      md.use(taskLists)
      // Show [1] every time a source is cited, not [1:2], [1:3] and so on
      md.renderer.rules.footnote_caption = (tokens, idx) => `[${tokens[idx].meta.id + 1}]`
      // A plain arrow instead of the default emoji-style back link
      md.renderer.rules.footnote_anchor = (tokens, idx, _options, env, slf) => {
        let id = slf.rules.footnote_anchor_name!(tokens, idx, _options, env, slf)
        if (tokens[idx].meta.subId > 0) id += `:${tokens[idx].meta.subId}`
        const label = env.relativePath?.startsWith('ar/') ? 'العودة إلى النص' : 'Back to text'
        return ` <a href="#fnref${id}" class="footnote-backref" aria-label="${label}">&#8593;</a>`
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
          { text: 'First 30 days', link: '/checklist' },
          { text: 'How we source', link: '/sourcing' },
          { text: 'Help wanted', link: '/help-wanted' }
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
    },
    ar: {
      label: 'العربية',
      lang: 'ar',
      dir: 'rtl',
      link: '/ar/',
      title: 'العيش في قطر',
      description: 'دليل عملي للمقيمين في قطر، كل معلومة فيه مربوطة بمصدرها الرسمي، بالعربية والإنجليزية.',
      themeConfig: {
        nav: [
          { text: 'الدليل', link: '/ar/guide/', activeMatch: '^/ar/guide/' },
          { text: 'أول 30 يومًا', link: '/ar/checklist' },
          { text: 'كيف نوثّق', link: '/ar/sourcing' },
          { text: 'نحتاج مساعدتك', link: '/ar/help-wanted' }
        ],
        sidebar: {
          '/ar/guide/': [{ text: 'كل المواضيع', link: '/ar/guide/' }, ...sidebar('ar')]
        },
        editLink: {
          pattern: `${repo}/edit/main/docs/:path`,
          text: 'اقترح تصحيحًا على GitHub'
        },
        outline: { level: [2, 3], label: 'في هذه الصفحة' },
        docFooter: { prev: 'السابق', next: 'التالي' },
        darkModeSwitchLabel: 'المظهر',
        lightModeSwitchTitle: 'التبديل إلى الوضع الفاتح',
        darkModeSwitchTitle: 'التبديل إلى الوضع الداكن',
        sidebarMenuLabel: 'القائمة',
        returnToTopLabel: 'العودة إلى الأعلى',
        langMenuLabel: 'تغيير اللغة',
        notFound: {
          title: 'الصفحة غير موجودة',
          quote: 'ربما نُقلت هذه الصفحة أو تغيّر عنوانها.',
          linkLabel: 'العودة إلى الصفحة الرئيسية',
          linkText: 'الصفحة الرئيسية'
        },
        footer: {
          message:
            'هذا الدليل ليس استشارة قانونية. تأكد دائمًا من الصفحة الرسمية المذكورة في المصادر. المحتوى بترخيص CC BY 4.0 والشيفرة بترخيص MIT.',
          copyright: 'حقوق النشر 2026 Mohaned Elhagar والمساهمون'
        }
      }
    }
  },

  themeConfig: {
    logo: { src: '/favicon.svg', alt: '' },
    socialLinks: [{ icon: 'github', link: repo }],
    search: {
      provider: 'local',
      options: {
        locales: { ar: { translations: searchTranslations } },
        miniSearch: {
          options: { processTerm: normalizeTerm },
          searchOptions: { fuzzy: 0.2, prefix: true, boost: { title: 4, text: 2, titles: 1 } }
        }
      }
    }
  }
})
