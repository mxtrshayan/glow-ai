// frontend/js/main.js — App entry point: wires all modules together

import { initWeather, initWeatherToggle } from './weather.js';
import { initUpload, initColorPicker, initPillGroups, collectFormData, validateForm } from './form.js';
import { displayResults } from './results.js';
import { scrollTo } from './utils.js';

const API_URL = '/analyze';

// ── Boot ───────────────────────────────────────────────────
document.addEventListener('DOMContentLoaded', async () => {
  initUpload();
  initColorPicker();
  initPillGroups();
  initWeatherToggle();

  // Weather is fetched asynchronously in the background
  initWeather().catch(console.warn);

  // Form submit
  const form = document.getElementById('makeupForm');
  if (form) form.addEventListener('submit', handleSubmit);

  // Retry button
  const retryBtn = document.getElementById('retryBtn');
  if (retryBtn) retryBtn.addEventListener('click', handleRetry);
});

// ── Submit Handler ─────────────────────────────────────────
async function handleSubmit(e) {
  e.preventDefault();
  if (!validateForm()) return;

  const form             = document.getElementById('makeupForm');
  const loadingOverlay   = document.getElementById('loadingOverlay');
  const resultsContainer = document.getElementById('resultsContainer');
  const event            = document.getElementById('event')?.value;
  const timeOfDay        = document.getElementById('time_of_day')?.value;

  // Show loading
  form.style.display = 'none';
  loadingOverlay.style.display = 'block';
  resultsContainer.style.display = 'none';

  try {
    const formData = collectFormData();
    const response = await fetch(API_URL, { method: 'POST', body: formData });

    if (!response.ok) throw new Error(`Server error: ${response.status}`);

    const data = await response.json();
    console.log('✅ GlowAI Response:', data);

    loadingOverlay.style.display = 'none';
    resultsContainer.style.display = 'block';

    displayResults(data, event, timeOfDay);
    scrollTo(resultsContainer);

  } catch (err) {
    console.error('API Error:', err);
    loadingOverlay.style.display = 'none';
    form.style.display = 'flex';

    let errEl = document.getElementById('apiError');
    if (!errEl) {
      errEl = document.createElement('p');
      errEl.id = 'apiError';
      errEl.style.cssText = 'color:#C0392B;text-align:center;font-size:.85rem;margin-top:.5rem;padding:1rem;background:#FEE;border-radius:8px;border:1px solid #F5C6CB;';
      document.querySelector('.submit-area')?.appendChild(errEl);
    }
    errEl.textContent = `❌ Something went wrong: ${err.message}`;
    setTimeout(() => { errEl.textContent = ''; }, 6000);
  }
}

// ── Retry Handler ──────────────────────────────────────────
function handleRetry() {
  const resultsContainer = document.getElementById('resultsContainer');
  const form             = document.getElementById('makeupForm');
  const grid             = document.getElementById('resultsGrid');

  if (resultsContainer) resultsContainer.style.display = 'none';
  if (form)             form.style.display = 'flex';
  if (grid)             grid.innerHTML = '';

  window.scrollTo({ top: 0, behavior: 'smooth' });
}
