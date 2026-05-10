// ── Config ────────────────────────────────────────────────
const API_URL = 'http://localhost:8000/analyze';

// ── Image Upload & Drag-Drop ──────────────────────────────
const uploadZone = document.getElementById('uploadZone');
const imageInput = document.getElementById('imageInput');
const uploadContent = document.getElementById('uploadContent');
const uploadPreview = document.getElementById('uploadPreview');
const previewImg = document.getElementById('previewImg');
const removeImgBtn = document.getElementById('removeImg');

uploadZone.addEventListener('dragover', e => { e.preventDefault(); uploadZone.classList.add('drag-over'); });
uploadZone.addEventListener('dragleave', () => uploadZone.classList.remove('drag-over'));
uploadZone.addEventListener('drop', e => {
  e.preventDefault();
  uploadZone.classList.remove('drag-over');
  const file = e.dataTransfer.files[0];
  if (file && file.type.startsWith('image/')) showPreview(file);
});

uploadZone.addEventListener('click', e => {
  if (e.target.closest('.btn-remove') || e.target.closest('.upload-preview')) return;
  if (uploadPreview.style.display === 'none') imageInput.click();
});

imageInput.addEventListener('change', () => {
  if (imageInput.files[0]) showPreview(imageInput.files[0]);
});

function showPreview(file) {
  const reader = new FileReader();
  reader.onload = e => {
    previewImg.src = e.target.result;
    uploadContent.style.display = 'none';
    uploadPreview.style.display = 'block';
  };
  reader.readAsDataURL(file);
}

removeImgBtn.addEventListener('click', () => {
  imageInput.value = '';
  previewImg.src = '';
  uploadPreview.style.display = 'none';
  uploadContent.style.display = 'block';
});

// ── Color Picker ──────────────────────────────────────────
const colorInput = document.getElementById('outfit_color');
const colorLabel = document.getElementById('colorLabel');

colorInput.addEventListener('input', () => {
  colorLabel.textContent = colorInput.value.toUpperCase();
});

document.querySelectorAll('.preset').forEach(p => {
  p.addEventListener('click', () => {
    colorInput.value = p.dataset.color;
    colorLabel.textContent = p.dataset.color.toUpperCase();
  });
});

// ── Form Submit ───────────────────────────────────────────
const form = document.getElementById('makeupForm');
const loadingOverlay = document.getElementById('loadingOverlay');
const resultsContainer = document.getElementById('resultsContainer');
const retryBtn = document.getElementById('retryBtn');
const resultsSubtitle = document.getElementById('resultsSubtitle');

form.addEventListener('submit', async e => {
  e.preventDefault();

  const event = document.getElementById('event').value;
  const timeOfDay = document.getElementById('time_of_day').value;
  if (!event || !timeOfDay) {
    alert('Please select an Event Type and Time of Day.');
    return;
  }

  const formData = new FormData();
  if (imageInput.files[0]) formData.append('image', imageInput.files[0]);

  const skinTone = document.querySelector('input[name="skin_tone"]:checked');
  formData.append('skin_tone', skinTone ? skinTone.value : '');
  formData.append('event', event);
  formData.append('time_of_day', timeOfDay);
  formData.append('outfit_color', colorInput.value);

  // Show loading
  form.style.display = 'none';
  loadingOverlay.style.display = 'block';
  resultsContainer.style.display = 'none';

  try {
    const response = await fetch(API_URL, { method: 'POST', body: formData });
    if (!response.ok) throw new Error(`Server error: ${response.status}`);

    const data = await response.json();
    console.log('✅ API Response:', data); // debug

    loadingOverlay.style.display = 'none';
    resultsContainer.style.display = 'block';
    
    // Pass the form data and AI data to rendering function
    displayResults(data, event, timeOfDay);

    // Smooth scroll to results
    resultsContainer.scrollIntoView({ behavior: 'smooth', block: 'start' });

  } catch (err) {
    console.error('API Error:', err);
    loadingOverlay.style.display = 'none';
    form.style.display = 'flex';
    alert(`Something went wrong: ${err.message}\n\nMake sure your FastAPI server is running on http://localhost:8000`);
  }
});

// ── Retry ─────────────────────────────────────────────────
retryBtn.addEventListener('click', () => {
  resultsContainer.style.display = 'none';
  form.style.display = 'flex';
  document.getElementById('resultsGrid').innerHTML = '';
  window.scrollTo({ top: 0, behavior: 'smooth' });
});

// ── Build Card Helper ─────────────────────────────────────
function buildCard(icon, title, items, tip, extraClass = '', showSwatch = true) {
  const card = document.createElement('div');
  card.className = `result-card ${extraClass}`;

  let itemsHTML = items
    .filter(item => item.value && item.value.toString().trim() !== '')
    .map(item => {
      const color = showSwatch ? extractColor(item.value) : null;
      const swatchHTML = color
        ? `<span class="result-swatch" style="background:${color};"></span>`
        : `<span class="result-dot"><i class="fa-solid fa-circle-small"></i></span>`;
      return `
        <div class="result-item">
          ${swatchHTML}
          <span class="result-text">
            <span class="result-label">${item.label}:</span> ${item.value}
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

// ── Display Results ───────────────────────────────────────
function displayResults(data, event, timeOfDay) {
  const resultsGrid = document.getElementById('resultsGrid');
  const resultsSubtitle = document.getElementById('resultsSubtitle');
  
  // Clear previous results
  resultsGrid.innerHTML = '';

  if (!data || (data.status !== "success" && data.status !== "fallback")) {
    resultsGrid.innerHTML = "<p>Something went wrong analyzing your look.</p>";
    return;
  }

  // Update Subtitle with Skin Analysis
  const skin = data.skin_analysis;
  let subtitleText = `${capitalize(event)} · ${capitalize(timeOfDay)}`;
  if (skin && skin.detected_tone) {
      subtitleText += ` <br> <span style="font-size: 0.9em; opacity: 0.8;">Skin: ${capitalize(skin.detected_tone)} | Undertone: ${capitalize(skin.undertone)} | Finish: ${capitalize(skin.finish)}</span>`;
  }
  resultsSubtitle.innerHTML = subtitleText;

  // 1. Face Card
  if (data.face) {
    resultsGrid.appendChild(buildCard(
      'fa-solid fa-face-smile', 'Face',
      [
        { label: 'Foundation', value: data.face.foundation },
        { label: 'Concealer', value: data.face.concealer },
        { label: 'Blush', value: data.face.blush },
        { label: 'Highlight', value: data.face.highlight },
        { label: 'Contour', value: data.face.contour }
      ],
      data.face.tip
    ));
  }

  // 2. Eyes Card
  if (data.eyes) {
    resultsGrid.appendChild(buildCard(
      'fa-solid fa-eye', 'Eyes',
      [
        { label: 'Eyeshadow', value: data.eyes.eyeshadow },
        { label: 'Eyeliner', value: data.eyes.eyeliner },
        { label: 'Mascara', value: data.eyes.mascara },
        { label: 'Brows', value: data.eyes.brows }
      ],
      data.eyes.tip
    ));
  }

// 3. Lips Card
  if (data.lips) {
    resultsGrid.appendChild(buildCard(
      'fa-solid fa-heart', // <--- Changed from 'fa-solid fa-lips'
      'Lips',
      [
        { label: 'Liner', value: data.lips.liner },
        { label: 'Lipstick', value: data.lips.lipstick },
        { label: 'Gloss', value: data.lips.gloss }
      ],
      data.lips.tip
    ));
  }
  // 4. Outfit Card (Swatches turned off)
  if (data.outfit) {
    resultsGrid.appendChild(buildCard(
      'fa-solid fa-shirt', 'Outfit',
      [
        { label: 'Dressing', value: data.outfit.dressing },
        { label: 'Dupatta', value: data.outfit.dupatta }
      ],
      null, '', false 
    ));
  }

  // 5. Accessories Card (Swatches turned off)
  if (data.accessories) {
    resultsGrid.appendChild(buildCard(
      'fa-solid fa-gem', 'Accessories',
      [
        { label: 'Jewellery', value: data.accessories.jewellery },
        { label: 'Bag', value: data.accessories.bag },
        { label: 'Sandals', value: data.accessories.sandals }
      ],
      null, '', false
    ));
  }

  // Overall Tip Injection
  if (data.overall_tip) {
    const tipDiv = document.createElement('div');
    tipDiv.style.gridColumn = '1 / -1';
    tipDiv.style.textAlign = 'center';
    tipDiv.style.padding = '1.5rem';
    tipDiv.style.background = 'var(--primary-light, #FDF2F8)'; // Fallback pink if variable missing
    tipDiv.style.color = 'var(--text, #333)';
    tipDiv.style.borderRadius = '12px';
    tipDiv.style.marginTop = '1rem';
    tipDiv.style.border = '1px dashed var(--primary, #D4A0C0)';
    tipDiv.innerHTML = `<strong>✨ Pro Tip:</strong> ${data.overall_tip}`;
    resultsGrid.appendChild(tipDiv);
  }
}

// ── Helpers ───────────────────────────────────────────────
function extractColor(text) {
  if (!text) return '#E8A0B4';
  const hex = text.match(/#[0-9A-Fa-f]{6}/);
  if (hex) return hex[0];
  
  const map = {
    'pink': '#F4A7B9', 'rose': '#E8839A', 'nude': '#D4A598',
    'red': '#C0392B', 'berry': '#8E2157', 'coral': '#E8735A',
    'peach': '#FFCBA4', 'brown': '#8B5E3C', 'mauve': '#C4879A',
    'plum': '#6B3A5A', 'gold': '#C9A96E', 'bronze': '#CD7F32',
    'champagne': '#F5E6C8', 'beige': '#E8D5B7', 'taupe': '#8B7B6B',
    'black': '#2C2C2C', 'white': '#F5F5F5', 'silver': '#C0C0C0',
    'copper': '#B87333', 'orange': '#E67E22', 'yellow': '#F4D03F',
    'green': '#27AE60', 'purple': '#8E44AD', 'blue': '#2980B9',
    'ivory': '#FFFFF0', 'caramel': '#C68642', 'terracotta': '#C0724A',
    'maroon': '#800000', 'mustard': '#E1AD01', 'emerald': '#50C878'
  };
  
  const lower = text.toLowerCase();
  for (const [k, v] of Object.entries(map)) {
    if (lower.includes(k)) return v;
  }
  return '#E8A0B4'; 
}

function capitalize(str) {
  if (!str) return '';
  return str.replace(/_/g, ' ').replace(/\b\w/g, c => c.toUpperCase());
}