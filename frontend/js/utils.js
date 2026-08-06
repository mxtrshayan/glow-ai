// frontend/js/utils.js — Shared utility functions

/**
 * Capitalise each word in a string, replacing underscores with spaces.
 */
export function capitalize(str) {
  if (!str) return '';
  return str.replace(/_/g, ' ').replace(/\b\w/g, c => c.toUpperCase());
}

/**
 * Extract a representative CSS color from a text description.
 */
export function extractColor(text) {
  if (!text) return '#E8A0B4';
  const hex = text.match(/#[0-9A-Fa-f]{6}/);
  if (hex) return hex[0];

  const map = {
    'porcelain': '#FAF0E6', 'ivory': '#FFFFF0', 'porce': '#FAF0E6',
    'very fair': '#FDDBB4', 'fair':  '#F5C89A', 'light': '#EEB98A',
    'pink': '#F4A7B9', 'rose': '#E8839A', 'nude': '#D4A598',
    'red': '#C0392B', 'berry': '#8E2157', 'coral': '#E8735A',
    'peach': '#FFCBA4', 'brown': '#8B5E3C', 'mauve': '#C4879A',
    'plum': '#6B3A5A', 'gold': '#C9A96E', 'bronze': '#CD7F32',
    'champagne': '#F5E6C8', 'beige': '#E8D5B7', 'taupe': '#8B7B6B',
    'black': '#2C2C2C', 'white': '#F5F5F5', 'silver': '#C0C0C0',
    'copper': '#B87333', 'orange': '#E67E22', 'yellow': '#F4D03F',
    'green': '#27AE60', 'purple': '#8E44AD', 'blue': '#2980B9',
    'caramel': '#C68642', 'terracotta': '#C0724A', 'maroon': '#800000',
    'mustard': '#E1AD01', 'emerald': '#50C878', 'teal': '#008080',
    'lavender': '#967BB6', 'mint': '#98FF98', 'sage': '#8FBC8F',
    'fuchsia': '#FF00FF', 'dusty rose': '#DCAE96', 'blush': '#DE5D83',
    'burgundy': '#800020', 'olive': '#808000', 'navy': '#001F5B',
    'magenta': '#FF00A0', 'lilac': '#C8A2C8', 'indigo': '#4B0082',
    'tan': '#D2B48C', 'honey': '#C9A84C', 'amber': '#FFBF00',
    'chestnut': '#954535', 'hazel': '#8E7618', 'grey': '#808080',
    'gray': '#808080',
  };

  const lower = text.toLowerCase();
  // Try multi-word matches first
  for (const [k, v] of Object.entries(map)) {
    if (lower.includes(k)) return v;
  }
  return '#E8A0B4';
}

/**
 * Smoothly scroll element into view.
 */
export function scrollTo(el) {
  el.scrollIntoView({ behavior: 'smooth', block: 'start' });
}
