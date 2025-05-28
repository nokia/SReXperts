/**
 * Copyright 2025 Nokia
 * Licensed under the BSD 3-Clause License.
 * SPDX-License-Identifier: BSD-3-Clause
 */

document.addEventListener('DOMContentLoaded', () => {
  const form = document.getElementById('submitFeedback')

  if(form !== null) {
    const url = window.location.href.split('/').filter(Boolean)
    const stars = document.querySelectorAll('.star')
    let selectedRating = 0

    const highlightStars = (count) => {
      stars.forEach((star, i) => {
        star.style.color = i < count ? '#facc15' : '#d1d5db' // yellow-400 and gray-300
      })
    }

    stars.forEach((star, index) => {
      // Highlight stars on hover
      star.addEventListener('mouseover', () => {
        highlightStars(index + 1)
      })

      // Reset to selected on mouse out
      star.addEventListener('mouseout', () => {
        highlightStars(selectedRating)
      })

      // Set selected rating on click
      star.addEventListener('click', () => {
        selectedRating = index + 1
        highlightStars(selectedRating)
        document.getElementById("rating").value = selectedRating
      })
    })

    form.addEventListener('submit', function (event) {
      event.preventDefault()

      const formData = new FormData(form)
      let payload = Object.fromEntries(formData.entries())

      let { achieved, graded, ...rest } = payload
      payload = {
        ...rest,
        achieved: achieved?.toLowerCase() === "yes",
        graded: graded?.toLowerCase() === "yes"
      }

      let title = document.title
      title = title.substring(0, title.lastIndexOf('-')).trim()
      const timestamp = Date.now()
      const userHash = getCookie('visitor_id')
      payload = {...payload, userHash, timestamp}

      if (url.length >= 3) {
        const stream = url[2].toUpperCase()
        const difficulty = url.length > 3 ? url[3].toUpperCase() : ''
        payload = { ...payload, useCase: { title, stream, difficulty } }
      } else if (url.length < 3) {
        payload = { ...payload, useCase: { title: 'Home', stream: '', difficulty: '' } }
      }

      //console.log('Feedback submitted with:', JSON.stringify(payload, null, 2))

      fetch('https://tracker.srexperts.net/api/register/feedback', {
        method: 'POST', body: JSON.stringify(payload)
      }).then(response => {
        if (response.ok) {
          alert('[Success] Feedback submitted successfully!')
        } else {
          alert('[Error] Issue submitting feedback. Kindly contact Admin.')
        }
      })
    })
  }
})
