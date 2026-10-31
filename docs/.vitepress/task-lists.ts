import type MarkdownIt from 'markdown-it'

// Turns "- [ ] Do this" list items into real checkboxes, for the printable
// checklist. Each box gets a stable id so ticks can be remembered locally.
export function taskLists(md: MarkdownIt) {
  md.core.ruler.after('inline', 'task-lists', (state) => {
    const tokens = state.tokens
    let count = 0
    for (let i = 2; i < tokens.length; i++) {
      const inline = tokens[i]
      if (inline.type !== 'inline') continue
      if (tokens[i - 1].type !== 'paragraph_open' || tokens[i - 2].type !== 'list_item_open') continue
      const match = inline.content.match(/^\[([ xX])\]\s+/)
      if (!match || !inline.children?.length) continue

      const first = inline.children[0]
      if (first.type !== 'text' || !first.content.startsWith(match[0].trimEnd())) continue
      first.content = first.content.slice(match[0].trimEnd().length).replace(/^\s+/, '')

      const id = `task-${++count}`
      const checked = match[1] !== ' ' ? ' checked' : ''
      const box = new state.Token('html_inline', '', 0)
      box.content = `<input type="checkbox" class="task-box" id="${id}" data-task="${id}"${checked}><label for="${id}" class="task-label">`
      const close = new state.Token('html_inline', '', 0)
      close.content = '</label>'
      inline.children.unshift(box)
      inline.children.push(close)

      tokens[i - 2].attrJoin('class', 'task-item')
      for (let j = i - 3; j >= 0; j--) {
        if (tokens[j].type === 'bullet_list_open' || tokens[j].type === 'ordered_list_open') {
          if (tokens[j].level === tokens[i - 2].level - 1) {
            if (!(tokens[j].attrGet('class') ?? '').includes('task-list')) tokens[j].attrJoin('class', 'task-list')
            break
          }
        }
      }
    }
    return true
  })
}
