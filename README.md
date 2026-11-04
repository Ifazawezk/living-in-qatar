<div align="center">

<img src="assets/banner.png" alt="Living in Qatar: a practical guide for residents in English and Arabic, where every claim links to the official page it comes from" width="100%">

<br><br>

[![Official sources](https://img.shields.io/badge/official_sources-106-8a1538)](docs/sourcing.md)
[![Content license](https://img.shields.io/badge/content-CC_BY_4.0-lightgrey)](LICENSE-CONTENT)
[![Code license](https://img.shields.io/badge/code-MIT-blue)](LICENSE)

</div>

A free guide to living in Qatar as a resident, in English and Arabic. Every claim links to the official page it comes from, with the month it was last checked.

[Read the guide](https://ifazawezk.github.io/living-in-qatar/) · [اقرأ الدليل بالعربية](https://ifazawezk.github.io/living-in-qatar/ar/) · [First 30 days checklist](https://ifazawezk.github.io/living-in-qatar/checklist) · [Help wanted](docs/help-wanted.md)

It is general information, not legal, immigration, medical or financial advice, and it is not run by or connected to any government body. Rules, fees and procedures change and the guide can be wrong or out of date, so confirm on the linked official page before you act, and for anything important ask the authority directly. The authors accept no liability for decisions based on it.

## Topics

If you just arrived, start with arriving and visas, the residence permit and QID, Metrash and the [first 30 days checklist](docs/checklist.md).

There are 15 topics, each in English and Arabic, backed by 106 official pages and 262 source citations.

| Topic | بالعربية | Sources |
| --- | --- | --- |
| [Arriving and visas](docs/guide/arriving-and-visas.md) | [الوصول والتأشيرات](docs/ar/guide/arriving-and-visas.md) | 10 |
| [Residence permit and QID](docs/guide/residence-permit-and-qid.md) | [رخصة الإقامة والبطاقة الشخصية](docs/ar/guide/residence-permit-and-qid.md) | 11 |
| [Metrash](docs/guide/metrash.md) | [مطراش](docs/ar/guide/metrash.md) | 14 |
| [Family visas](docs/guide/family-visas.md) | [التأشيرات العائلية](docs/ar/guide/family-visas.md) | 7 |
| [Housing and renting](docs/guide/housing-and-utilities.md) | [السكن والإيجار](docs/ar/guide/housing-and-utilities.md) | 7 |
| [Health care and insurance](docs/guide/health.md) | [الرعاية الصحية والتأمين](docs/ar/guide/health.md) | 13 |
| [Phone and internet](docs/guide/phone-and-internet.md) | [الهاتف والإنترنت](docs/ar/guide/phone-and-internet.md) | 11 |
| [Banking and money transfers](docs/guide/banking-and-money.md) | [البنوك وتحويل الأموال](docs/ar/guide/banking-and-money.md) | 7 |
| [Work and labour rights](docs/guide/work-and-labour-rights.md) | [العمل وحقوق العمال](docs/ar/guide/work-and-labour-rights.md) | 3 |
| [Cost of living basics](docs/guide/cost-of-living.md) | [أساسيات تكاليف المعيشة](docs/ar/guide/cost-of-living.md) | 8 |
| [Public holidays and Ramadan working hours](docs/guide/holidays-and-ramadan.md) | [العطلات الرسمية وساعات العمل في رمضان](docs/ar/guide/holidays-and-ramadan.md) | 5 |
| [Driving licence and traffic rules](docs/guide/driving.md) | [رخصة القيادة وقواعد المرور](docs/ar/guide/driving.md) | 9 |
| [Getting around: Metro, buses and taxis](docs/guide/transport.md) | [التنقل: المترو والحافلات وسيارات الأجرة](docs/ar/guide/transport.md) | 6 |
| [Education and schools](docs/guide/education.md) | [التعليم والمدارس](docs/ar/guide/education.md) | 9 |
| [Emergencies and important numbers](docs/guide/emergencies.md) | [الطوارئ والأرقام المهمة](docs/ar/guide/emergencies.md) | 11 |

The [checklist](docs/checklist.md) prints, and [Help wanted](docs/help-wanted.md) lists everything that couldn't be confirmed yet.

Some official sources are old. The labour page rests on a National Human Rights Committee booklet from December 2021, plus a January 2006 English copy of the law for the gratuity amount, because the current law text and Ministry of Labour pages couldn't be opened when it was written. Check the current labour law text before relying on that page. Some Ministry of Interior service pages are old too, and the pages that depend on them say so.

## Sources

Only official pages are cited: Government of Qatar sites, and public bodies and licensed operators for their own services. The full list is in [`scripts/official_domains.txt`](scripts/official_domains.txt). News, forums, blogs, relocation firms and law firm articles are never cited.

Each claim has a footnote to the exact page it came from, which was opened and read before it was cited, and each footnote ends with the month it was last checked (the latest round was 2026-10). Fees are usually linked rather than copied, because amounts change. When two official pages disagree, as they do on passport validity, the guide says so and cites both. Anything that couldn't be confirmed goes on the Help wanted list instead of being guessed. The full rules are in [How we source things](docs/sourcing.md).

Two scripts, both standard library Python, check this:

```bash
python scripts/lint_content.py     # fails if any paragraph has no official source
python scripts/check_links.py      # visits every source link and reports problems
```

The lint fails if a paragraph, list item or table row has no official source, if a footnote has no date or links to a domain that isn't on the list, or if the English and Arabic pages cite different sources.

The link checker sorts every link into `ok`, `moved`, `changed` (the title differs from [the saved baseline](scripts/link_baseline.json)), `blocked` (the site turned away an automated visitor), `dead` or `unreachable`. Latest run:

```text
checking 106 links on 24 sites
0 dead, 3 unreachable, 0 moved, 0 changed, 5 blocked, 98 ok (106 links)
```

`blocked` and `unreachable` don't mean the page is gone. Some sites turn away scripts or didn't answer from the network the check ran on, so a person has to open those links in a browser.

## The site

| Desktop, English | Desktop, Arabic |
| --- | --- |
| ![Guide page in English with last checked date and footnotes](assets/screenshots/desktop-en-topic.png) | ![Guide page in Arabic, laid out right to left](assets/screenshots/desktop-ar-topic.png) |

| Arabic search, typed with ه instead of ة | Phone, Arabic, dark |
| --- | --- |
| ![Arabic search results for a query spelled without ta marbuta](assets/screenshots/desktop-ar-search.png) | ![Arabic home page on a phone in dark mode](assets/screenshots/phone-ar-dark.png) |

The Arabic pages are laid out right to left with their own typeface and interface text, not mirrored from English. Search runs in your browser and ignores differences in hamza, ta marbuta, alif maqsura, diacritics and the definite article, and it reads ٩٩٩ as 999. The site works on a phone and has a dark mode. Every page has an edit link and a "Report something out of date" link.

There are no ads, no sign-up, no analytics, no cookies and no third-party scripts or fonts. Your theme and checklist ticks are stored in your own browser.

## Run it locally

You need Node.js 18 or newer and Python 3.10 or newer.

```bash
npm install
npm run dev     # http://localhost:5173/living-in-qatar/
npm run build   # production build in docs/.vitepress/dist
npm test        # search tests against the build, then the Python tests
```

The site is set up for GitHub Pages at `/living-in-qatar/`.

## Contributing

Corrections from people who live here keep the guide useful. Every change needs an official source, so read [CONTRIBUTING.md](CONTRIBUTING.md) first. The quickest route is the edit link at the bottom of any page. To report a mistake, use "Report something out of date" at the top of the page and include the official link that shows the right information.

Good first contributions:

- Pick an item from [Help wanted](docs/help-wanted.md) and link the official page.
- Open the `blocked` links in a browser and confirm they still say what the guide says.
- Improve a sentence of Arabic that reads like a translation.

Planned:

- [ ] Check the labour page against the law text and current Ministry of Labour pages
- [ ] Close the top gaps in Help wanted: Metrash registration, licensed exchange houses, rental law, resident health insurance
- [ ] Main traffic rules, from official sources
- [ ] New topics: domestic workers, starting a business, buying a car, leaving Qatar for good
- [ ] Scheduled link checks that open an issue when a source changes
- [ ] A downloadable PDF of the whole guide
- [ ] More languages for the communities who need this most, starting with Hindi, Urdu, Malayalam and Filipino

## License

Content in `docs/` is licensed under [CC BY 4.0](LICENSE-CONTENT): you can reuse it if you credit the guide, link back and keep the sources. Code is licensed under the [MIT License](LICENSE).

Copyright (c) 2026 Mohaned Elhagar
