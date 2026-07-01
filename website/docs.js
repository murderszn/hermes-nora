function wireDiscordLinks() {
  const invite = window.NORA_LINKS?.discord;
  if (!invite) return;

  document.querySelectorAll('[data-discord-link]').forEach((el) => {
    el.href = invite;
  });
}

function initScrollProgress() {
  const bar = document.getElementById('scroll-progress');
  if (!bar) return;

  const update = () => {
    const max = document.documentElement.scrollHeight - window.innerHeight;
    const progress = max > 0 ? window.scrollY / max : 0;
    bar.style.transform = `scaleX(${Math.min(progress, 1)})`;
  };

  window.addEventListener('scroll', update, { passive: true });
  update();
}

wireDiscordLinks();
initScrollProgress();