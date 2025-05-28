/**
 * Copyright 2025 Nokia
 * Licensed under the BSD 3-Clause License.
 * SPDX-License-Identifier: BSD-3-Clause
 */

document.addEventListener('DOMContentLoaded', () => {
  const url = window.location.href.split('/').filter(Boolean)

  const updateScroll = (scrollHeading) => {
    const scrollTop = window.scrollY;
    const docHeight = document.documentElement.scrollHeight - window.innerHeight
    let scrollPercent = Math.round((scrollTop / docHeight) * 100)
    if(!scrollPercent) scrollPercent = 0

    let title = document.title
    title = title.substring(0, title.lastIndexOf('-')).trim()
    const timestamp = Date.now()
    const userHash = getCookie('visitor_id')
    let payload = { userHash, scrollHeading, scrollPercent, timestamp }

    if (url.length >= 3) {
      const stream = url[2].toUpperCase()
      const difficulty = url.length > 3 ? url[3].toUpperCase() : ''
      payload = { ...payload, useCase: { stream, difficulty } }
    } else if (url.length < 3) {
      payload = { ...payload, useCase: { stream: '', difficulty: '', title: 'Home' } }
    }
    if (url.length >= 3) {
      const stream = url[2].toUpperCase()
      const difficulty = url.length > 3 ? url[3].toUpperCase() : ''
      payload = { ...payload, useCase: { title, stream, difficulty } }
    } else if (url.length < 3) {
      payload = { ...payload, useCase: { title: 'Home', stream: '', difficulty: '' } }
    }
    
    //console.log('Scroll info:', JSON.stringify(payload, null, 2))

    fetch('https://tracker.srexperts.net/api/register/scroll', {
      method: 'POST', body: JSON.stringify(payload)
    }).then(response => {
      if (response.ok) {
        //console.log('[Success] Scroll info submitted successfully!')
      } else {
        console.log('[Error] Issue submitting scroll info. Kindly contact Admin.')
      }
    })
  }

  // HEADING PROGRESS
  const headings = document.querySelectorAll('h1, h2, h3, h4, h5, h6')
  const headingObserver = new IntersectionObserver((entries) => {
    entries.forEach(entry => {
      if (entry.isIntersecting) {
        const textContent = entry.target.textContent.trim()
        updateScroll(textContent.slice(0, -1))
      }
    })
  }, {
    root: null,
    rootMargin: '0px 0px -30% 0px',
    threshold: 0
  })

  headings.forEach(heading => headingObserver.observe(heading))

  // END OF PAGE
  const footer = document.querySelectorAll('footer')[0]
  const footerObserver = new IntersectionObserver((entries) => {
    entries.forEach(entry => {
      if (entry.isIntersecting) {
        updateScroll("END")
      }
    })
  }, {
    root: null,
    rootMargin: '0px',
    threshold: 0
  })
  footerObserver.observe(footer)
})
