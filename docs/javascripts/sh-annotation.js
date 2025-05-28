/**
 * Copyright 2025 Nokia
 * Licensed under the BSD 3-Clause License.
 * SPDX-License-Identifier: BSD-3-Clause
 */

// this script is used to remove extra leading space when annotating shell code blocks ending with `\`
// character. See https://github.com/squidfunk/mkdocs-material/issues/3846 for more info.
document$.subscribe(() => {
    const tags = document.querySelectorAll("code .se")
    tags.forEach(tag => {
        if (tag.innerText.startsWith("\\")) {
            tag.innerText = "\\"
        }
    })
})