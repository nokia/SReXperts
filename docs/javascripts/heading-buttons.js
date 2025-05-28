/**
 * Copyright 2025 Nokia
 * Licensed under the BSD 3-Clause License.
 * SPDX-License-Identifier: BSD-3-Clause
 */

document.addEventListener('DOMContentLoaded', () => {
  const url = window.location.href.split('/').filter(Boolean)
  const startH2 = document.getElementById('tasks')
  const h3s = []

  let el = startH2.nextElementSibling

  while (el && el.tagName !== 'H2') {
    if (el.tagName === 'H3') h3s.push(el)
    el = el.nextElementSibling
  }

  startButtonStyle = 'padding: 2px 10px; font-size: 12px; border-radius: 9999px; margin-top: 20px;'

  h3s.forEach(heading => {
    const btn = document.createElement('button')
    btn.innerText = 'Start'
    btn.className = 'md-button md-button--primary'
    btn.style = startButtonStyle
    if(heading.tagName)

    // Add your custom logic here
    btn.addEventListener('click', () => {
      btn.innerText = 'Started'
      btn.style = startButtonStyle + ' background-color: green;'

      let title = document.title
      title = title.substring(0, title.lastIndexOf('-')).trim()
      const timestamp = Date.now()
      const userHash = getCookie('visitor_id')
      let payload = { userHash, timestamp, startedTask: heading.innerText, started: true }

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
      
      //console.log('Task started:', JSON.stringify(payload, null, 2))

      fetch('https://tracker.srexperts.net/api/register/scroll', {
        method: 'POST', body: JSON.stringify(payload)
      }).then(response => {
        if (response.ok) {
          //console.log('[Success] Task started submitted successfully!')
        } else {
          console.log('[Error] Issue submitting task started info. Kindly contact Admin.')
        }
      })
    })

    // Wrap in a flex container
    const wrapper = document.createElement('div')
    wrapper.style = 'display: flex; align-items: center;'
    heading.parentNode.insertBefore(wrapper, heading)
    wrapper.appendChild(heading)
    wrapper.appendChild(btn)
  })
})
