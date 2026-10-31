// Search term normalisation for English and Arabic.
//
// The local search index (MiniSearch) runs every indexed word and every query
// word through this function, so people find "البطاقة الصحية" whether they
// type it with or without hamza, diacritics or the definite article.
//
// VitePress sends this function to the browser as source text, so it must not
// use anything defined outside its own body.
export function normalizeTerm(term) {
  let word = term.toLowerCase()

  // Arabic-Indic and Persian digits to 0-9, so "٩٩٩" finds "999"
  word = word.replace(/[٠-٩]/g, (d) => String(d.charCodeAt(0) - 0x0660))
  word = word.replace(/[۰-۹]/g, (d) => String(d.charCodeAt(0) - 0x06f0))

  word = word
    .replace(/[ً-ٰٟ]/g, '') // harakat and dagger alif
    .replace(/ـ/g, '') // tatweel
    .replace(/[آأإٱ]/g, 'ا') // alif with hamza or madda
    .replace(/ى/g, 'ي') // alif maqsura to ya
    .replace(/ة/g, 'ه') // ta marbuta to ha
    .replace(/ؤ/g, 'و') // waw with hamza
    .replace(/ئ/g, 'ي') // ya with hamza

  // Drop the definite article and the common one-letter prefixes before it,
  // but keep short words intact ("الله", "ال" alone and so on stay as they are).
  const prefix = word.match(/^(?:[وفبكل]?ال|لل)/)
  if (prefix && word.length - prefix[0].length >= 3) {
    word = word.slice(prefix[0].length)
  }

  return word || null
}
