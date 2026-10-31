// Tests for the Arabic-aware search. Run with:  node --test tests/
//
// The first group checks the normaliser on its own. The second loads the real
// search index from the last build (npm run build) and runs a few queries the
// way the site does; it is skipped when there is no build yet.
import { test } from 'node:test'
import assert from 'node:assert/strict'
import fs from 'node:fs'
import path from 'node:path'
import { fileURLToPath, pathToFileURL } from 'node:url'
import MiniSearch from 'minisearch'
import { normalizeTerm } from '../docs/.vitepress/normalize.mjs'

const root = path.resolve(path.dirname(fileURLToPath(import.meta.url)), '..')

test('lowercases English words', () => {
  assert.equal(normalizeTerm('Metrash'), 'metrash')
})

test('treats hamza forms of alif the same', () => {
  assert.equal(normalizeTerm('إقامة'), normalizeTerm('اقامة'))
  assert.equal(normalizeTerm('أسرة'), normalizeTerm('اسرة'))
  assert.equal(normalizeTerm('آخر'), normalizeTerm('اخر'))
})

test('treats ta marbuta and ha, alif maqsura and ya the same', () => {
  assert.equal(normalizeTerm('البطاقة'), normalizeTerm('البطاقه'))
  assert.equal(normalizeTerm('مستشفى'), normalizeTerm('مستشفي'))
})

test('ignores diacritics and tatweel', () => {
  assert.equal(normalizeTerm('الصِّحَّة'), normalizeTerm('الصحة'))
  assert.equal(normalizeTerm('مطـــراش'), normalizeTerm('مطراش'))
})

test('drops the definite article and joined prefixes', () => {
  assert.equal(normalizeTerm('البطاقة'), normalizeTerm('بطاقة'))
  assert.equal(normalizeTerm('والإقامة'), normalizeTerm('إقامة'))
  assert.equal(normalizeTerm('للعمال'), normalizeTerm('عمال'))
})

test('keeps short words whole', () => {
  assert.equal(normalizeTerm('الله'), 'الله')
  assert.equal(normalizeTerm('الى'), 'الي')
})

test('reads Arabic-Indic digits as Western digits', () => {
  assert.equal(normalizeTerm('٩٩٩'), '999')
  assert.equal(normalizeTerm('۲۰۲۶'), '2026')
})

test('uses nothing from outside its own body, so VitePress can ship it to the browser', () => {
  const copy = new Function(`return ${normalizeTerm.toString()}`)()
  assert.equal(copy('الإقامة'), normalizeTerm('الإقامة'))
})

function loadIndex(locale) {
  const dir = path.join(root, 'docs', '.vitepress', 'dist', 'assets', 'chunks')
  if (!fs.existsSync(dir)) return null
  const file = fs.readdirSync(dir).find((name) => name.startsWith(`@localSearchIndex${locale}.`))
  return file ? path.join(dir, file) : null
}

async function search(locale, query) {
  const file = loadIndex(locale)
  const { default: json } = await import(pathToFileURL(file).href)
  const index = MiniSearch.loadJSON(json, {
    fields: ['title', 'titles', 'text'],
    storeFields: ['title', 'titles'],
    processTerm: normalizeTerm,
    searchOptions: { fuzzy: 0.2, prefix: true, boost: { title: 4, text: 2, titles: 1 } }
  })
  return index.search(query)
}

const built = loadIndex('ar') !== null
const skip = built ? false : 'no build yet, run npm run build first'

test('Arabic search finds pages whatever the spelling', { skip }, async () => {
  const withHamza = await search('ar', 'الإقامة')
  const withoutHamza = await search('ar', 'اقامه')
  assert.ok(withHamza.length > 0, 'no results for الإقامة')
  assert.deepEqual(
    withoutHamza.slice(0, 5).map((r) => r.id),
    withHamza.slice(0, 5).map((r) => r.id)
  )
})

test('Arabic search finds the emergency number typed in Arabic digits', { skip }, async () => {
  const results = await search('ar', '٩٩٩')
  assert.ok(results.length > 0)
})

test('English search still works', { skip }, async () => {
  const results = await search('root', 'residence permit')
  assert.ok(results.length > 0)
})
