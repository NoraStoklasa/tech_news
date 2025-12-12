document.addEventListener('DOMContentLoaded', () => {
  const container = document.getElementById('news-container')
  const articlesList = document.getElementById('articles-list')
  const loadingIndicator = document.getElementById('loading-indicator')
  const sentinel = document.getElementById('scroll-sentinel')
  if (!container || !articlesList || !sentinel) return

  const emptyState = document.getElementById('empty-state')
  const pageSize = parseInt(container.dataset.initialLimit || '5', 10)
  let nextOffset = parseInt(container.dataset.nextOffset || '0', 10)
  let hasMore = (container.dataset.hasMore || 'false') === 'true'
  let loading = false

  articlesList.addEventListener('click', (event) => {
    const link = event.target.closest('.read-more-link')
    if (!link) return
    event.preventDefault()
    const summaryText = link.closest('.summary-text')
    const shortText = summaryText.querySelector('.summary-short')
    const fullText = summaryText.querySelector('.summary-full')
    const isOpening = fullText.style.display === 'none'
    shortText.style.display = isOpening ? 'none' : 'inline'
    fullText.style.display = isOpening ? 'inline' : 'none'
    link.textContent = isOpening ? 'Read less' : 'Read more'
  })

  function createArticleItem(article) {
    const li = document.createElement('li')
    li.className = 'article-item'

    const titleEl = document.createElement('h2')
    titleEl.textContent = article.title || ''
    li.appendChild(titleEl)

    const row = document.createElement('div')
    row.className = 'article-row'

    const text = document.createElement('div')
    text.className = 'article-text'

    const summary = document.createElement('p')
    summary.className = 'summary-text'

    const shortSpan = document.createElement('span')
    shortSpan.className = 'summary-short'
    shortSpan.textContent = article.first_sentence || ''
    summary.appendChild(shortSpan)

    const fullSpan = document.createElement('span')
    fullSpan.className = 'summary-full'
    fullSpan.style.display = 'none'
    fullSpan.textContent = article.summary || ''
    summary.appendChild(fullSpan)

    if (article.summary && article.summary !== article.first_sentence) {
      const link = document.createElement('a')
      link.href = '#'
      link.className = 'read-more-link'
      link.textContent = 'Read more'
      summary.appendChild(link)
    }

    text.appendChild(summary)

    const fullLink = document.createElement('a')
    fullLink.href = article.url || '#'
    fullLink.target = '_blank'
    fullLink.rel = 'noopener noreferrer'
    fullLink.textContent = 'Read full article'
    text.appendChild(fullLink)

    const date = document.createElement('p')
    date.className = 'article-date'
    date.textContent = `Published on: ${article.created_at || ''}`
    text.appendChild(date)

    const category = document.createElement('p')
    category.className = 'article-category'
    category.textContent = `Category: ${article.category || 'Unknown'}`
    text.appendChild(category)

    row.appendChild(text)

    const media = document.createElement('div')
    media.className = 'article-media'
    if (article.image_url) {
      const img = document.createElement('img')
      img.src = article.image_url
      img.alt = article.image_alt || article.title || 'Article image'
      img.className = 'article-image'
      media.appendChild(img)
    }
    row.appendChild(media)

    li.appendChild(row)
    return li
  }

  function appendArticles(list) {
    list.forEach((article) => {
      const item = createArticleItem(article)
      articlesList.appendChild(item)
    })
  }

  async function fetchMoreArticles() {
    if (loading || !hasMore) return
    loading = true
    if (loadingIndicator) loadingIndicator.style.display = 'block'

    try {
      const response = await fetch(
        `/api/articles?limit=${pageSize}&offset=${nextOffset}`
      )
      if (!response.ok) throw new Error('Failed to load articles')

      const data = await response.json()
      appendArticles(data.articles || [])
      nextOffset = data.next_offset ?? nextOffset + (data.articles?.length || 0)
      hasMore = Boolean(data.has_more)

      if (emptyState && articlesList.children.length > 0) {
        emptyState.style.display = 'none'
      }
    } catch (error) {
      console.error(error)
      hasMore = false
    } finally {
      loading = false
      if (loadingIndicator) loadingIndicator.style.display = 'none'
    }
  }

  const observer = new IntersectionObserver(
    (entries) => {
      entries.forEach((entry) => {
        if (entry.isIntersecting) {
          fetchMoreArticles()
        }
      })
    },
    { rootMargin: '400px 0px' }
  )

  observer.observe(sentinel)
})
