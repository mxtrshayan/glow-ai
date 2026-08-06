// frontend/js/results.js — Render all result cards

import { capitalize, extractColor } from './utils.js';

const WEATHER_ICONS_MAP = {
  rainy:    'fa-cloud-rain',
  hot_humid: 'fa-sun',
  cold:     'fa-snowflake',
  mild:     'fa-cloud-sun',
};

/* ── Main render function ─────────────────────────────────── */
export function displayResults(data, event, timeOfDay) {
  const grid     = document.getElementById('resultsGrid');
  const subtitle = document.getElementById('resultsSubtitle');

  grid.innerHTML = '';

  if (!data || (data.status !== 'success' && data.status !== 'fallback')) {
    grid.innerHTML = '<p style="text-align:center;color:#A8849A;">Something went wrong analyzing your look.</p>';
    return;
  }

  // ── Fallback notice ──────────────────────────────────────
  if (data.status === 'fallback') {
    const notice = document.createElement('div');
    notice.className = 'fallback-notice';
    notice.innerHTML = '<i class="fa-solid fa-circle-info"></i> AI unavailable — showing curated recommendations for your look.';
    grid.appendChild(notice);
  }

  // ── Results subtitle ─────────────────────────────────────
  const skin = data.skin_analysis;
  let subtitleHTML = `${capitalize(event)} · ${capitalize(timeOfDay)}`;
  if (skin?.detected_tone) {
    const swatchColor = extractColor(skin.detected_tone);
    subtitleHTML += `
      <br>
      <span class="skin-summary-pill">
        <span class="skin-swatch-sm" style="background:${swatchColor};"></span>
        ${capitalize(skin.detected_tone)} · ${capitalize(skin.undertone)} Undertone · ${capitalize(skin.finish)} Finish
      </span>`;
  }
  if (subtitle) subtitle.innerHTML = subtitleHTML;

  // ── Weather banner ───────────────────────────────────────
  if (data.weather_tip && data.inputs_received?.weather !== 'not provided') {
    const cat = data.inputs_received?.weather_category || 'mild';
    const iconClass = WEATHER_ICONS_MAP[cat] || 'fa-cloud-sun';
    const banner = document.createElement('div');
    banner.className = `weather-alert-banner ${cat}`;
    banner.innerHTML = `<i class="fa-solid ${iconClass}"></i> <strong>Weather Tip:</strong> ${data.weather_tip}`;
    grid.appendChild(banner);
  }

  // ── Face card ────────────────────────────────────────────
  if (data.face) {
    grid.appendChild(buildCard('fa-solid fa-face-smile', 'Face & Base', [
      { label: 'Primer',      value: data.face.primer },
      { label: 'Foundation',  value: data.face.foundation },
      { label: 'Concealer',   value: data.face.concealer },
      { label: 'Blush',       value: data.face.blush },
      { label: 'Highlight',   value: data.face.highlight },
      { label: 'Contour',     value: data.face.contour },
      { label: 'Setting',     value: data.face.setting },
    ], data.face.tip));
  }

  // ── Eyes card ────────────────────────────────────────────
  if (data.eyes) {
    grid.appendChild(buildCard('fa-solid fa-eye', 'Eyes', [
      { label: 'Eyeshadow', value: data.eyes.eyeshadow },
      { label: 'Eyeliner',  value: data.eyes.eyeliner },
      { label: 'Mascara',   value: data.eyes.mascara },
      { label: 'Brows',     value: data.eyes.brows },
    ], data.eyes.tip));
  }

  // ── Lips card ────────────────────────────────────────────
  if (data.lips) {
    const lipsItems = [
      { label: 'Liner',    value: data.lips.liner },
      { label: 'Lipstick', value: data.lips.lipstick, chip: data.lips.shade_name },
      { label: 'Gloss',    value: data.lips.gloss },
    ];
    grid.appendChild(buildCard('fa-solid fa-heart', 'Lips', lipsItems, data.lips.tip));
  }

  // ── Outfit card ──────────────────────────────────────────
  if (data.outfit) {
    grid.appendChild(buildCard('fa-solid fa-shirt', 'Outfit', [
      { label: 'Dressing',   value: data.outfit.dressing },
      { label: 'Dupatta',    value: data.outfit.dupatta },
      { label: 'Footwear',   value: data.outfit.footwear },
      { label: 'Style Note', value: data.outfit.style_note },
    ], null, '', false));
  }

  // ── Accessories card ─────────────────────────────────────
  if (data.accessories) {
    grid.appendChild(buildCard('fa-solid fa-gem', 'Accessories', [
      { label: 'Jewellery', value: data.accessories.jewellery },
      { label: 'Bag',       value: data.accessories.bag },
      { label: 'Extra',     value: data.accessories.extra },
    ], null, '', false));
  }

  // ── Brands card ──────────────────────────────────────────
  if (data.brands) {
    grid.appendChild(buildCard('fa-solid fa-tag', 'Recommended Brands', [
      { label: 'Foundation', value: data.brands.foundation_brand },
      { label: 'Lips',       value: data.brands.lip_brand },
      { label: 'Eyes',       value: data.brands.eye_brand },
      { label: 'Blush',      value: data.brands.blush_brand },
      { label: 'Budget Pick', value: data.brands.drugstore_pick },
    ], data.brands.tip, '', false));
  }

  // ── Lens card ────────────────────────────────────────────
  if (data.lens) {
    const lensColor = extractColor(data.lens.color);
    grid.appendChild(buildCard('fa-solid fa-eye', 'Contact Lenses', [
      { label: 'Colour',  value: data.lens.color },
      { label: 'Brand',   value: data.lens.brand_suggestion },
      { label: 'Why',     value: data.lens.reason },
    ], data.lens.tip, '', true));
  }

  // ── Hair / Hijab card ────────────────────────────────────
  if (data.hair_hijab) {
    const hijabMode = data.inputs_received?.hijab === 'yes';
    grid.appendChild(buildCard(
      hijabMode ? 'fa-solid fa-user-hijab' : 'fa-solid fa-scissors',
      hijabMode ? 'Hijab Style' : 'Hairstyle',
      [
        { label: 'Style',       value: data.hair_hijab.style },
        { label: 'Colour Tip',  value: data.hair_hijab.color_suggestion },
        { label: 'Accessory',   value: data.hair_hijab.accessory },
      ],
      data.hair_hijab.tip, '', false
    ));
  }

  // ── Overall tip banner ───────────────────────────────────
  if (data.overall_tip) {
    const banner = document.createElement('div');
    banner.className = 'overall-tip-banner';
    banner.innerHTML = `<strong>✨ Your Look:</strong> ${data.overall_tip}`;
    grid.appendChild(banner);
  }
}

/* ── Card Builder ─────────────────────────────────────────── */
function buildCard(icon, title, items, tip, extraClass = '', showSwatch = true) {
  const card = document.createElement('div');
  card.className = `result-card ${extraClass}`;

  const itemsHTML = items
    .filter(item => item.value && String(item.value).trim() !== '' && String(item.value).toLowerCase() !== 'n/a')
    .map(item => {
      const color = showSwatch ? extractColor(item.value) : null;
      const swatchHTML = color
        ? `<span class="result-swatch" style="background:${color};"></span>`
        : `<span class="result-dot"><i class="fa-solid fa-circle" style="font-size:.4rem;color:var(--rose-dark);margin-top:.35rem;"></i></span>`;

      const chipHTML = item.chip
        ? `<span class="shade-chip"><i class="fa-solid fa-droplet" style="font-size:.55rem;"></i> ${item.chip}</span>`
        : '';

      return `
        <div class="result-item">
          ${swatchHTML}
          <span class="result-text">
            <span class="result-label">${item.label}:</span> ${item.value}${chipHTML}
          </span>
        </div>`;
    }).join('');

  card.innerHTML = `
    <div class="result-card-icon"><i class="${icon}"></i></div>
    <h3>${title}</h3>
    ${itemsHTML}
    ${tip ? `<div class="result-tip">💡 ${tip}</div>` : ''}
  `;
  return card;
}
