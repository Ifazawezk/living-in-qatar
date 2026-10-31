# Contributing

Thanks for helping. Corrections from people who live in Qatar are what keep this guide useful.

There is one rule above all the others: **every fact needs an official source.** If you cannot link to an official page that says it, it does not go in the guide, however sure you are. That is the whole value of this project, so please do not take it personally if a pull request is held back for a missing source.

## Quick ways to help

- **Something is out of date.** Open an issue with the page, what is wrong, and a link to the official page that shows the right information. The "Report something out of date" link at the top of each page fills in most of this for you.
- **You can fix it yourself.** Use "Suggest a correction on GitHub" at the bottom of any page. GitHub will walk you through a fork and a pull request without installing anything.
- **Pick an item from [Help wanted](docs/help-wanted.md).** These are things readers ask about that we could not confirm from an official page yet.
- **Check blocked links by hand.** Some government sites turn away automated checks. The link report lists them as `blocked`. Open them in a normal browser and tell us whether they still say what the guide says.
- **Review the Arabic.** If a sentence reads like a translation, suggest a better one.

## Sourcing rules

1. **Official sources only.** Government of Qatar sites (gov.qa and its ministries and authorities), official law texts on almeezan.qa, and public bodies for their own services (Hamad Medical Corporation, Kahramaa, Mowasalat and Karwa, Qatar Rail, Hamad International Airport, Qatar Post, Visit Qatar) and the National Human Rights Committee. Licensed telecom operators count only for facts about their own services. The list lives in [`scripts/official_domains.txt`](scripts/official_domains.txt).
2. **Not sources:** news sites, forums, blogs, Facebook groups, relocation companies, law firm articles, insurers' country guides, Wikipedia, chatbots. They can tell you what to look up. They cannot be the citation.
3. **Link the exact page,** not the home page of the ministry, so a reader can confirm the fact in one click.
4. **Read it yourself.** Only cite a page you opened and read. Do not cite a page because a search result or a summary said it contains something.
5. **Write it in your own words.** Paraphrase. Do not paste whole paragraphs from official sites.
6. **Do not invent or estimate numbers.** Fees, fines, days, salaries and deadlines must be written on the page you cite. For fees, prefer linking the official fee page over copying the amount, because fees change.
7. **Date it.** Every footnote ends with `Last checked: YYYY-MM` (Arabic: `آخر تحقق: YYYY-MM`), the month you read the page.
8. **Not sure? Leave it out** and add it to [Help wanted](docs/help-wanted.md) with what you know and what is missing.

To add a new official domain, explain in the pull request who runs the site and why it is the authority for the facts it supports.

## Page format

Each topic is one Markdown file in `docs/guide/` (English) and the same file name in `docs/ar/guide/` (Arabic).

```markdown
---
title: Residence permit and QID
description: One plain sentence on what the page covers.
lastChecked: 2026-10
---

# Residence permit and QID

Do the medical checkup within thirty days of entering Qatar.[^moi-visa-tips]

## Sources

[^moi-visa-tips]: Ministry of Interior, [Tips & Guidelines](https://portal.moi.gov.qa/...). Last checked: 2026-10.
```

- Every paragraph, list item, quote and table row needs at least one footnote (or an inline link) to an official page. Put the footnote right after the claim it supports.
- One footnote name per page you cite, short and descriptive: `[^moi-visa-tips]`, `[^hmc-health-card]`.
- The Arabic page uses the same footnote names as the English page. The lint fails if they differ, which is how we keep the two languages in step.
- A line that only points to other pages of the guide is fine without a source: `See also: [Metrash](./metrash.md).`

## Writing style

- Plain, practical and short. Write for a friend who arrived last week and has a lot to sort out.
- Use "you". Prefer steps and short lists over long paragraphs.
- No long dashes, no emoji, no marketing words.
- Arabic is written as Arabic, not translated word by word. Use the terms that the official Qatari Arabic pages use, and Western digits (0 to 9) for numbers and dates.

## Run it locally

You need Node.js 18 or newer and Python 3.10 or newer.

```bash
npm install
npm run dev          # site at http://localhost:5173/living-in-qatar/
npm run build        # production build in docs/.vitepress/dist
npm run lint         # every paragraph has an official source
npm test             # search tests (needs a build) and the Python tests
npm run links        # visit every source link (takes a few minutes)
```

On macOS and Linux, use `python3` if `python` is not on your path:

```bash
python3 scripts/lint_content.py
python3 -m unittest discover -s tests
python3 scripts/check_links.py --markdown link-report.md
```

## Before you open a pull request

- [ ] Every new or changed claim has a footnote to an official page you read yourself.
- [ ] Footnotes have this month's `Last checked` date.
- [ ] The English and Arabic pages both have the change, or the pull request says which one still needs it.
- [ ] `npm run lint` passes.
- [ ] `npm run build` passes.

If you can only do the English side, that is fine. Say so in the pull request and someone else can do the Arabic.

## Code of conduct

Be kind and assume good faith. People come to this guide when they are new, stressed or dealing with something urgent. Keep discussions about the facts and the sources.
