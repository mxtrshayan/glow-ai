// frontend/js/form.js — Form UI interactions (upload, swatches, pills, color picker)

import { currentWeatherData, useWeather } from './weather.js';

/* ── Image Upload & Drag-Drop ─────────────────────────────── */
export function initUpload() {
  const zone    = document.getElementById('uploadZone');
  const input   = document.getElementById('imageInput');
  const content = document.getElementById('uploadContent');
  const preview = document.getElementById('uploadPreview');
  const img     = document.getElementById('previewImg');
  const remove  = document.getElementById('removeImg');

  if (!zone) return;

  zone.addEventListener('dragover', e => { e.preventDefault(); zone.classList.add('drag-over'); });
  zone.addEventListener('dragleave', () => zone.classList.remove('drag-over'));
  zone.addEventListener('drop', e => {
    e.preventDefault(); zone.classList.remove('drag-over');
    const file = e.dataTransfer.files[0];
    if (file && file.type.startsWith('image/')) showPreview(file, img, content, preview);
  });

  zone.addEventListener('click', e => {
    if (e.target.closest('.btn-remove') || e.target.closest('.upload-preview')) return;
    if (preview.style.display === 'none' || !preview.style.display) input.click();
  });

  input.addEventListener('change', () => {
    if (input.files[0]) showPreview(input.files[0], img, content, preview);
  });

  remove.addEventListener('click', () => {
    input.value = ''; img.src = '';
    preview.style.display = 'none';
    content.style.display = 'block';
  });
}

function showPreview(file, img, content, preview) {
  const reader = new FileReader();
  reader.onload = e => {
    img.src = e.target.result;
    content.style.display = 'none';
    preview.style.display = 'block';
  };
  reader.readAsDataURL(file);
}

/* ── Color Picker & Presets ───────────────────────────────── */
export function initColorPicker() {
  const colorInput  = document.getElementById('outfit_color');
  const colorLabel  = document.getElementById('colorLabel');
  const colorSearch = document.getElementById('colorSearch');

  if (!colorInput) return;

  colorInput.addEventListener('input', () => {
    colorLabel.textContent = colorInput.value.toUpperCase();
    clearSelectedPreset();
  });

  // Preset swatches
  document.querySelectorAll('.preset').forEach(p => {
    p.addEventListener('click', () => {
      colorInput.value = p.dataset.color;
      colorLabel.textContent = (p.dataset.name || p.dataset.color).toUpperCase();
      document.querySelectorAll('.preset').forEach(x => x.classList.remove('selected'));
      p.classList.add('selected');
    });
  });

  // Color name search
  if (colorSearch) {
    colorSearch.addEventListener('input', () => {
      const q = colorSearch.value.trim().toLowerCase();
      document.querySelectorAll('.preset').forEach(p => {
        const name = (p.dataset.name || p.title || '').toLowerCase();
        p.style.display = (!q || name.includes(q)) ? '' : 'none';
      });
    });
  }
}

function clearSelectedPreset() {
  document.querySelectorAll('.preset').forEach(p => p.classList.remove('selected'));
}

/* ── Pill Group Buttons ───────────────────────────────────── */
export function initPillGroups() {
  document.querySelectorAll('[data-pill-group]').forEach(group => {
    const name = group.dataset.pillGroup;
    const btns = group.querySelectorAll('.pill-btn');
    const hidden = document.getElementById(`${name}_value`);

    btns.forEach(btn => {
      btn.addEventListener('click', () => {
        btns.forEach(b => b.classList.remove('active'));
        btn.classList.add('active');
        if (hidden) hidden.value = btn.dataset.value;
      });
    });
  });
}

/* ── Collect all form values for submission ───────────────── */
export function collectFormData() {
  const imageInput = document.getElementById('imageInput');
  const fd = new FormData();

  if (imageInput && imageInput.files[0]) fd.append('image', imageInput.files[0]);

  // Standard fields
  const skinTone = document.querySelector('input[name="skin_tone"]:checked');
  fd.append('skin_tone',   skinTone ? skinTone.value : '');
  fd.append('event',       document.getElementById('event')?.value || '');
  fd.append('time_of_day', document.getElementById('time_of_day')?.value || '');
  fd.append('outfit_color', document.getElementById('outfit_color')?.value || '');

  // New fields
  fd.append('undertone',        document.getElementById('undertone_value')?.value || '');
  fd.append('skin_type',        document.getElementById('skin_type_value')?.value || '');
  fd.append('hijab',            document.getElementById('hijab_value')?.value || 'no');
  fd.append('style_preference', document.getElementById('style_pref_value')?.value || 'both');
  fd.append('owned_items',      document.getElementById('owned_items')?.value || '');

  // Weather (only if user opted in)
  if (useWeather && currentWeatherData && !currentWeatherData.error) {
    fd.append('weather_condition', currentWeatherData.condition || '');
    fd.append('weather_temp',      currentWeatherData.temp_c || 0);
    fd.append('weather_humidity',  currentWeatherData.humidity || 0);
    fd.append('weather_category',  currentWeatherData.category || '');
  }

  return fd;
}

/* ── Validate required fields ─────────────────────────────── */
export function validateForm() {
  const event      = document.getElementById('event')?.value;
  const timeOfDay  = document.getElementById('time_of_day')?.value;
  if (!event || !timeOfDay) {
    showFormError('Please select an Event Type and Time of Day.');
    return false;
  }
  return true;
}

function showFormError(msg) {
  let el = document.getElementById('formError');
  if (!el) {
    el = document.createElement('p');
    el.id = 'formError';
    el.style.cssText = 'color:#C0392B;font-size:.85rem;text-align:center;margin-top:.5rem;';
    document.querySelector('.submit-area')?.appendChild(el);
  }
  el.textContent = msg;
  setTimeout(() => { el.textContent = ''; }, 4000);
}
