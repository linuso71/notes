(() => {
  const cacheLifetime = 5 * 60 * 1000;

  const updateStars = async (refresh = false) => {
    const link = document.querySelector('[data-repository-link]');
    if (!link) return;

    const repositoryPath = new URL(link.href).pathname.replace(/\/$/, '');
    const cacheKey = `repository-stars:${repositoryPath}`;
    let count;

    try {
      const cached = JSON.parse(sessionStorage.getItem(cacheKey));
      if (!refresh && cached && Date.now() - cached.updatedAt < cacheLifetime) {
        count = cached.count;
      }
    } catch {
      // Star counts also work when browser storage is unavailable.
    }

    if (!Number.isInteger(count) || count < 0) {
      try {
        const response = await fetch(`https://api.github.com/repos${repositoryPath}`, {
          headers: { Accept: 'application/vnd.github+json' },
          signal: AbortSignal.timeout(5000),
        });
        if (!response.ok) return;
        count = (await response.json()).stargazers_count;
        if (!Number.isInteger(count) || count < 0) return;
      } catch {
        // The repository link remains usable if GitHub cannot be reached.
        return;
      }

      try {
        sessionStorage.setItem(cacheKey, JSON.stringify({ count, updatedAt: Date.now() }));
      } catch {
        // Caching is optional.
      }
    }

    const label = `${count.toLocaleString()} ${count === 1 ? 'star' : 'stars'} on GitHub`;
    document.querySelectorAll('[data-repo-stars]').forEach((badge) => {
      badge.querySelector('[data-repo-star-count]').textContent = count.toLocaleString();
      badge.setAttribute('aria-label', label);
      badge.title = label;
      badge.hidden = false;
    });
    document.querySelectorAll('[data-repository-link]').forEach((anchor) => {
      anchor.setAttribute('aria-label', `${repositoryPath.slice(1)}, ${label} (opens in a new tab)`);
    });
  };

  let refreshAfterVisit = false;
  document.addEventListener('click', (event) => {
    if (event.target.closest('[data-repository-link], .repo-support__button')) {
      refreshAfterVisit = true;
    }
  });
  window.addEventListener('focus', () => {
    if (refreshAfterVisit) {
      refreshAfterVisit = false;
      updateStars(true);
    }
  });

  document$.subscribe(() => updateStars());
})();
