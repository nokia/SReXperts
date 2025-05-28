/**
 * Copyright 2025 Nokia
 * Licensed under the BSD 3-Clause License.
 * SPDX-License-Identifier: BSD-3-Clause
 */

function generateUUID() {
  return 'xxxxxxxx-xxxx-4xxx-yxxx-xxxxxxxxxxxx'.replace(/[xy]/g, function (c) {
    const r = Math.random() * 16 | 0,
          v = c === 'x' ? r : (r & 0x3 | 0x8)
    return v.toString(16)
  })
}

function setCookie(name, value) {
  document.cookie = `${name}=${encodeURIComponent(value)}; path=/`
}

function getCookie(name) {
  return document.cookie.split('; ').reduce((acc, pair) => {
    const [key, val] = pair.split('=')
    return key === name ? decodeURIComponent(val) : acc
  }, null);
}

document.addEventListener('DOMContentLoaded', () => {
  const vistorId = getCookie('visitor_id')
  if (!vistorId) {
    const id = generateUUID()
    setCookie('visitor_id', id)
    //console.log('Assigned new visitor ID:', id)
  } else {
    //console.log('Visitor ID already set:', vistorId)
  }
})