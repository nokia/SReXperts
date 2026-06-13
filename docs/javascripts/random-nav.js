/**
 * Copyright 2026 Nokia
 * Licensed under the BSD 3-Clause License.
 * SPDX-License-Identifier: BSD-3-Clause
 */

document.addEventListener("DOMContentLoaded", () => {
  // Keep sidebar order fixed on EDA docs (pedagogical sequence matters there).
  const firstSegment = window.location.pathname.split("/").filter(Boolean)[0];
  if (firstSegment === "eda") return;

  const SECTION_LABELS = new Set(["Beginner", "Intermediate", "Advanced"]);

  function shuffleList(list) {
    const items = Array.from(list.children);
    if (items.length < 2) return;
    for (let i = items.length - 1; i > 0; i--) {
      const j = Math.floor(Math.random() * (i + 1));
      [items[i], items[j]] = [items[j], items[i]];
    }
    items.forEach((item) => list.appendChild(item));
  }

  function sectionLabel(li) {
    const direct = li.querySelector(
      ":scope > a.md-nav__link, :scope > label.md-nav__link"
    );
    const fromLink = direct?.textContent?.trim();
    if (fromLink) return fromLink;
    const title = li.querySelector(":scope > .md-nav__title");
    return title?.textContent?.trim() ?? "";
  }

  function topLevelActiveSectionItem(primary) {
    const list = primary.querySelector(":scope > .md-nav__list");
    if (!list) return null;
    const marked = list.querySelector(":scope > .md-nav__item--active");
    if (marked) return marked;
    const anyActive = primary.querySelector(".md-nav__item--active");
    if (!anyActive) return null;
    for (const li of list.children) {
      if (li.matches("li.md-nav__item") && li.contains(anyActive)) return li;
    }
    return null;
  }

  // Shuffle only pages under Beginner / Intermediate / Advanced — not those headings.
  document.querySelectorAll(".md-nav--primary").forEach((primary) => {
    const activeRoot = topLevelActiveSectionItem(primary);
    if (!activeRoot) return;

    activeRoot.querySelectorAll("li.md-nav__item").forEach((li) => {
      const nestedList = li.querySelector(":scope > .md-nav > .md-nav__list");
      if (!nestedList) return;
      if (!SECTION_LABELS.has(sectionLabel(li))) return;
      shuffleList(nestedList);
    });
  });
});
