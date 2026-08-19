// frontend/js/tryon.js — Virtual Makeup Try-On Studio Module

let userPhotoDataUrl = null;
let currentResultDataUrl = null;
let debounceTimer = null;

const makeupConfig = {
  lipstick: { enabled: true, color: '#C8385A', opacity: 0.70, finish: 'satin' },
  blush:    { enabled: true, color: '#E07A7A', opacity: 0.35 },
  eyeshadow:{ enabled: true, color: '#8B5A2B', opacity: 0.45 },
  eyeliner: { enabled: true, color: '#1A1A1A', opacity: 0.85, style: 'winged' },
};

let currentViewerMode = 'split'; // 'split', 'after', 'before'

export function setUserPhoto(dataUrl) {
  userPhotoDataUrl = dataUrl;
}

export function getUserPhoto() {
  return userPhotoDataUrl;
}

export function openTryOnStudio(featureToFocus = null, aiData = null) {
  const modal = document.getElementById('tryonModal');
  if (!modal) return;

  // Prepopulate from AI recommendation data if available
  if (aiData) {
    if (aiData.lips?.hex) {
      makeupConfig.lipstick.color = aiData.lips.hex;
      makeupConfig.lipstick.enabled = true;
    }
    if (aiData.face?.blush_hex) {
      makeupConfig.blush.color = aiData.face.blush_hex;
      makeupConfig.blush.enabled = true;
    }
    if (aiData.eyes?.eyeshadow_hex) {
      makeupConfig.eyeshadow.color = aiData.eyes.eyeshadow_hex;
      makeupConfig.eyeshadow.enabled = true;
    }
    if (aiData.eyes?.eyeliner_hex) {
      makeupConfig.eyeliner.color = aiData.eyes.eyeliner_hex;
      makeupConfig.eyeliner.enabled = true;
    }
  }

  // If user clicked a specific feature try-on button
  if (featureToFocus) {
    // Optionally focus or enable only that feature if requested,
    // or ensure that feature is enabled and highlighted
    if (makeupConfig[featureToFocus]) {
      makeupConfig[featureToFocus].enabled = true;
    }
  }

  syncControlsUI();
  modal.classList.add('active');
  document.body.style.overflow = 'hidden';

  // Check if we have user photo
  if (!userPhotoDataUrl) {
    const previewImg = document.getElementById('previewImg');
    if (previewImg && previewImg.src && previewImg.src.startsWith('data:')) {
      userPhotoDataUrl = previewImg.src;
    }
  }

  const promptEl = document.getElementById('tryonUploadPrompt');
  const stageEl  = document.getElementById('tryonCompareStage');

  if (!userPhotoDataUrl) {
    if (promptEl) promptEl.style.display = 'flex';
    if (stageEl)  stageEl.style.display = 'none';
  } else {
    if (promptEl) promptEl.style.display = 'none';
    if (stageEl)  stageEl.style.display = 'block';
    triggerTryOn();
  }
}

export function closeTryOnStudio() {
  const modal = document.getElementById('tryonModal');
  if (modal) modal.classList.remove('active');
  document.body.style.overflow = '';
}

export function initTryOn() {
  const modal = document.getElementById('tryonModal');
  const closeBtn = document.getElementById('closeTryonBtn');
  if (!modal) return;

  if (closeBtn) closeBtn.addEventListener('click', closeTryOnStudio);

  // Close on outside click
  modal.addEventListener('click', e => {
    if (e.target === modal) closeTryOnStudio();
  });

  // Close on Escape key
  document.addEventListener('keydown', e => {
    if (e.key === 'Escape' && modal.classList.contains('active')) {
      closeTryOnStudio();
    }
  });

  // Modal photo upload fallback
  const modalUploadInput = document.getElementById('modalImageInput');
  const modalUploadBtn   = document.getElementById('modalUploadBtn');
  if (modalUploadBtn && modalUploadInput) {
    modalUploadBtn.addEventListener('click', () => modalUploadInput.click());
    modalUploadInput.addEventListener('change', e => {
      const file = e.target.files[0];
      if (file && file.type.startsWith('image/')) {
        const reader = new FileReader();
        reader.onload = ev => {
          userPhotoDataUrl = ev.target.result;
          document.getElementById('tryonUploadPrompt').style.display = 'none';
          document.getElementById('tryonCompareStage').style.display = 'block';
          triggerTryOn();
        };
        reader.readAsDataURL(file);
      }
    });
  }

  // Split Range Slider
  const sliderInput = document.getElementById('compareSliderInput');
  const afterPane   = document.getElementById('compareAfterPane');
  const sliderHandle= document.getElementById('compareSliderHandle');

  if (sliderInput) {
    sliderInput.addEventListener('input', e => {
      const val = e.target.value;
      if (afterPane) afterPane.style.width = `${val}%`;
      if (sliderHandle) sliderHandle.style.left = `${val}%`;
    });
  }

  // Mode buttons (Split, Before, After)
  document.querySelectorAll('[data-view-mode]').forEach(btn => {
    btn.addEventListener('click', () => {
      document.querySelectorAll('[data-view-mode]').forEach(b => b.classList.remove('active'));
      btn.classList.add('active');
      currentViewerMode = btn.dataset.viewMode;
      applyViewerMode();
    });
  });

  // Download button
  const downloadBtn = document.getElementById('downloadTryonBtn');
  if (downloadBtn) {
    downloadBtn.addEventListener('click', () => {
      const src = currentResultDataUrl || userPhotoDataUrl;
      if (!src) return;
      const a = document.createElement('a');
      a.href = src;
      a.download = 'GlowAI_Virtual_Makeup.jpg';
      document.body.appendChild(a);
      a.click();
      document.body.removeChild(a);
    });
  }

  // Bind Feature Controls
  bindFeatureControl('lipstick', {
    toggle: 'toggleLipstick',
    color: 'lipstickColor',
    hex: 'lipstickHex',
    opacity: 'lipstickOpacity',
    finish: 'lipstickFinish',
  });

  bindFeatureControl('blush', {
    toggle: 'toggleBlush',
    color: 'blushColor',
    hex: 'blushHex',
    opacity: 'blushOpacity',
  });

  bindFeatureControl('eyeshadow', {
    toggle: 'toggleEyeshadow',
    color: 'eyeshadowColor',
    hex: 'eyeshadowHex',
    opacity: 'eyeshadowOpacity',
  });

  bindFeatureControl('eyeliner', {
    toggle: 'toggleEyeliner',
    color: 'eyelinerColor',
    hex: 'eyelinerHex',
    opacity: 'eyelinerOpacity',
    style: 'eyelinerStyle',
  });
}

function bindFeatureControl(featureName, ids) {
  const toggleEl = document.getElementById(ids.toggle);
  const colorEl  = document.getElementById(ids.color);
  const hexEl    = document.getElementById(ids.hex);
  const opacEl   = document.getElementById(ids.opacity);
  const finishEl = ids.finish ? document.getElementById(ids.finish) : null;
  const styleEl  = ids.style ? document.getElementById(ids.style) : null;

  const card = toggleEl?.closest('.tryon-feature-card');

  if (toggleEl) {
    toggleEl.addEventListener('change', () => {
      makeupConfig[featureName].enabled = toggleEl.checked;
      if (card) card.classList.toggle('active', toggleEl.checked);
      debouncedTryOn();
    });
  }

  if (colorEl) {
    colorEl.addEventListener('input', () => {
      makeupConfig[featureName].color = colorEl.value;
      if (hexEl) hexEl.textContent = colorEl.value.toUpperCase();
      debouncedTryOn();
    });
  }

  if (opacEl) {
    opacEl.addEventListener('input', () => {
      makeupConfig[featureName].opacity = parseFloat(opacEl.value);
      debouncedTryOn();
    });
  }

  if (finishEl) {
    finishEl.addEventListener('change', () => {
      makeupConfig[featureName].finish = finishEl.value;
      debouncedTryOn();
    });
  }

  if (styleEl) {
    styleEl.addEventListener('change', () => {
      makeupConfig[featureName].style = styleEl.value;
      debouncedTryOn();
    });
  }
}

function syncControlsUI() {
  const syncMap = {
    lipstick: { toggle: 'toggleLipstick', color: 'lipstickColor', hex: 'lipstickHex', opacity: 'lipstickOpacity', finish: 'lipstickFinish' },
    blush:    { toggle: 'toggleBlush', color: 'blushColor', hex: 'blushHex', opacity: 'blushOpacity' },
    eyeshadow:{ toggle: 'toggleEyeshadow', color: 'eyeshadowColor', hex: 'eyeshadowHex', opacity: 'eyeshadowOpacity' },
    eyeliner: { toggle: 'toggleEyeliner', color: 'eyelinerColor', hex: 'eyelinerHex', opacity: 'eyelinerOpacity', style: 'eyelinerStyle' },
  };

  Object.entries(syncMap).forEach(([feat, ids]) => {
    const cfg = makeupConfig[feat];
    const toggleEl = document.getElementById(ids.toggle);
    const colorEl  = document.getElementById(ids.color);
    const hexEl    = document.getElementById(ids.hex);
    const opacEl   = document.getElementById(ids.opacity);
    const finishEl = ids.finish ? document.getElementById(ids.finish) : null;
    const styleEl  = ids.style ? document.getElementById(ids.style) : null;
    const card     = toggleEl?.closest('.tryon-feature-card');

    if (toggleEl) {
      toggleEl.checked = cfg.enabled;
      if (card) card.classList.toggle('active', cfg.enabled);
    }
    if (colorEl && cfg.color) colorEl.value = cfg.color;
    if (hexEl && cfg.color) hexEl.textContent = cfg.color.toUpperCase();
    if (opacEl && cfg.opacity !== undefined) opacEl.value = cfg.opacity;
    if (finishEl && cfg.finish) finishEl.value = cfg.finish;
    if (styleEl && cfg.style) styleEl.value = cfg.style;
  });
}

function debouncedTryOn() {
  clearTimeout(debounceTimer);
  debounceTimer = setTimeout(() => {
    triggerTryOn();
  }, 250);
}

async function triggerTryOn() {
  if (!userPhotoDataUrl) return;

  const loadingEl = document.getElementById('tryonLoading');
  const errorEl   = document.getElementById('tryonError');
  const imgBefore = document.getElementById('imgBefore');
  const imgAfter  = document.getElementById('imgAfter');

  if (loadingEl) loadingEl.style.display = 'flex';
  if (errorEl)   errorEl.style.display = 'none';

  if (imgBefore) imgBefore.src = userPhotoDataUrl;

  try {
    const payload = {
      image_b64: userPhotoDataUrl,
      makeup_config: makeupConfig,
    };

    const res = await fetch('/tryon', {
      method: 'POST',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify(payload),
    });

    if (!res.ok) throw new Error(`HTTP ${res.status}`);

    const result = await res.json();

    if (result.status === 'error') {
      throw new Error(result.message || 'Face detection failed');
    }

    currentResultDataUrl = result.image_b64;
    if (imgAfter) imgAfter.src = currentResultDataUrl;

    applyViewerMode();
  } catch (err) {
    console.error('Try-On error:', err);
    if (errorEl) {
      errorEl.textContent = `⚠️ ${err.message}`;
      errorEl.style.display = 'flex';
    }
  } finally {
    if (loadingEl) loadingEl.style.display = 'none';
  }
}

function applyViewerMode() {
  const afterPane   = document.getElementById('compareAfterPane');
  const sliderHandle= document.getElementById('compareSliderHandle');
  const sliderInput = document.getElementById('compareSliderInput');
  const badgeBefore = document.querySelector('.badge-before');
  const badgeAfter  = document.querySelector('.badge-after');

  if (!afterPane) return;

  if (currentViewerMode === 'split') {
    const val = sliderInput ? sliderInput.value : 50;
    afterPane.style.width = `${val}%`;
    if (sliderHandle) sliderHandle.style.display = 'flex';
    if (sliderInput)  sliderInput.style.display = 'block';
    if (badgeBefore)  badgeBefore.style.display = 'block';
    if (badgeAfter)   badgeAfter.style.display = 'block';
  } else if (currentViewerMode === 'after') {
    afterPane.style.width = '100%';
    if (sliderHandle) sliderHandle.style.display = 'none';
    if (sliderInput)  sliderInput.style.display = 'none';
    if (badgeBefore)  badgeBefore.style.display = 'none';
    if (badgeAfter)   badgeAfter.style.display = 'block';
  } else if (currentViewerMode === 'before') {
    afterPane.style.width = '0%';
    if (sliderHandle) sliderHandle.style.display = 'none';
    if (sliderInput)  sliderInput.style.display = 'none';
    if (badgeBefore)  badgeBefore.style.display = 'block';
    if (badgeAfter)   badgeAfter.style.display = 'none';
  }
}
