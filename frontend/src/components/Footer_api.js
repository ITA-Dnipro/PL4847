const CONTENT_ENDPOINT = '/api/content/landing/';
const SUBSCRIBE_ENDPOINT = '/api/subscribe/';

export async function fetchFooterContent(signal) {
  const res = await fetch(CONTENT_ENDPOINT, { signal });
  if (!res.ok) throw new Error(`Request failed: ${res.status}`);
  return res.json();
}

function getCsrfToken() {
  const match = document.cookie.match(/(?:^|;\s*)csrftoken=([^;]+)/);
  return match ? decodeURIComponent(match[1]) : '';
}

export async function subscribeToStartup(startupId) {
  const res = await fetch(SUBSCRIBE_ENDPOINT, {
    method: 'POST',
    headers: {
      'Content-Type': 'application/json',
      'X-CSRFToken': getCsrfToken(),
    },
    credentials: 'same-origin',
    body: JSON.stringify({ startup_id: startupId }),
  });

  if (res.ok) {
    return { ok: true, message: 'Дякуємо! Ви успішно підписалися на стартап.' };
  }

  const data = await res.json().catch(() => null);
  const message = data?.startup_id?.[0] || data?.detail || 'Не вдалося оформити підписку. Спробуйте ще раз.';
  return { ok: false, message };
}