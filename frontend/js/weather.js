// frontend/js/weather.js — Weather fetching, widget rendering, toggle logic

export let currentWeatherData = null;
export let useWeather = false;

const WEATHER_ICONS = {
  rainy:    'fa-cloud-rain',
  hot_humid: 'fa-sun',
  cold:     'fa-snowflake',
  mild:     'fa-cloud-sun',
};

/**
 * Attempt to get user's location and fetch weather.
 * Updates the header weather widget.
 */
export async function initWeather() {
  const widget = document.getElementById('weatherWidget');
  const toggleStrip = document.getElementById('weatherToggleStrip');

  if (!widget) return;

  if (!navigator.geolocation) {
    widget.innerHTML = '<i class="fa-solid fa-location-slash"></i> Location unavailable';
    return;
  }

  try {
    const position = await new Promise((resolve, reject) =>
      navigator.geolocation.getCurrentPosition(resolve, reject, { timeout: 8000 })
    );

    const { latitude: lat, longitude: lon } = position.coords;
    const res = await fetch(`/weather?lat=${lat}&lon=${lon}`);
    const data = await res.json();

    if (data.error) {
      widget.innerHTML = `<i class="fa-solid fa-triangle-exclamation"></i> ${data.error}`;
      return;
    }

    currentWeatherData = data;
    renderWeatherWidget(widget, data);

    // Show weather toggle strip
    if (toggleStrip) {
      toggleStrip.classList.add('visible');
      // Default: use weather = true
      setWeatherToggle(true);
    }

  } catch (err) {
    console.warn('Weather fetch failed:', err.message);
    widget.innerHTML = `<i class="fa-solid fa-cloud-slash"></i> Weather unavailable`;
  }
}

function renderWeatherWidget(widget, data) {
  const iconClass = WEATHER_ICONS[data.category] || 'fa-cloud';
  const badgeClass = `badge-${data.category}`;
  widget.innerHTML = `
    <i class="fa-solid ${iconClass}"></i>
    <span class="weather-temp">${data.temp_c}°C</span>
    <span class="weather-sep">·</span>
    <span>${data.condition}</span>
    <span class="weather-sep">·</span>
    <span class="weather-city">${data.city}, ${data.country}</span>
    <span class="weather-badge ${badgeClass}">${data.category.replace('_', ' ')}</span>
  `;
}

export function setWeatherToggle(value) {
  useWeather = value;
  const btnYes = document.getElementById('weatherYes');
  const btnNo  = document.getElementById('weatherNo');
  if (!btnYes || !btnNo) return;

  btnYes.classList.toggle('active-yes', value);
  btnYes.classList.toggle('toggle-pill', true);
  btnNo.classList.toggle('active-no', !value);
  btnNo.classList.toggle('toggle-pill', true);
}

export function initWeatherToggle() {
  const btnYes = document.getElementById('weatherYes');
  const btnNo  = document.getElementById('weatherNo');
  if (btnYes) btnYes.addEventListener('click', () => setWeatherToggle(true));
  if (btnNo)  btnNo.addEventListener('click',  () => setWeatherToggle(false));
}
