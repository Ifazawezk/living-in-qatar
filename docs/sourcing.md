---
title: How we source things
description: The rules every fact in this guide has to pass.
---

# How we source things

This guide has one rule: if we cannot point to an official page for a fact, the fact does not go in.

## What counts as official

- Government of Qatar websites: Hukoomi and the ministries, councils and authorities on gov.qa, such as the Ministry of Interior, the Ministry of Labour, the Ministry of Public Health and Qatar Central Bank.
- Official law texts on Al Meezan, the legal portal.
- Public bodies and state companies, for their own services: Hamad Medical Corporation, Kahramaa, Mowasalat (Karwa), Qatar Rail, Hamad International Airport, Qatar Post and Visit Qatar.
- The National Human Rights Committee, whose worker booklet supports the labour page.
- Licensed telecom operators, only for facts about their own services.

The full list is in [`scripts/official_domains.txt`](https://github.com/Ifazawezk/living-in-qatar/blob/main/scripts/official_domains.txt). News articles, forums, blogs, relocation companies and social media posts are never used as sources, even when they turn out to be right. They can be a useful hint about what to look up, nothing more.

## How a fact gets in

1. The official page is opened and read.
2. The fact is written in plain words, with a footnote to the exact page and the month it was checked.
3. The Arabic page cites the same footnotes. A check fails if the two languages cite different sources.
4. In the pull request, a script checks that every paragraph, list item and table row has an official source, and a reviewer opens each new link.

## Fees and numbers

Fees change more often than anything else, so we usually link to the official fee or service page instead of copying an amount. When a number does appear, such as an emergency number or a number of days of leave, it is written on the linked page.

## Keeping it current

- Every footnote ends with "Last checked" and a month.
- `python scripts/check_links.py` visits every source link. It reports links that are dead, links that now redirect somewhere else, and pages whose title changed since the last saved run.
- Some government sites block automated visitors. The checker lists those separately as "blocked" so a person can open them in a browser and confirm them by hand.
- `python scripts/lint_content.py --stale-after 12` warns about sources nobody has checked for a year.

## What we leave out

- Anything we could not confirm on an official page. Those items go on the help wanted list instead.
- Rent and grocery prices, rankings of schools or neighbourhoods, and opinions about employers. There is no official source for these, and they go stale quickly.

## Not legal advice

This is a community project. It is not run by, or connected to, any government body. It explains where to look and what the official pages say, in plain words. For a decision that matters, read the official page, and if your case is unusual, ask the authority itself.
