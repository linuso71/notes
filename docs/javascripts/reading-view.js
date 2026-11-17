(() => {
  const root = document.documentElement;
  const desktop = window.matchMedia('(min-width: 76.25em)');

  const update = () => {
    const sidebar = document.querySelector('.md-sidebar--primary');
    const drawer = document.querySelector('#__drawer');
    if (sidebar) sidebar.id = 'notes-sidebar';
    const expanded = desktop.matches ? !root.classList.contains('sidebar-hidden') : Boolean(drawer?.checked);
    document.querySelectorAll('[data-sidebar-toggle]').forEach((button) => {
      button.hidden = !sidebar || sidebar.hidden || (!desktop.matches && !expanded);
      button.setAttribute('aria-expanded', String(expanded));
      const label = expanded ? 'Collapse sidebar' : 'Expand sidebar';
      button.setAttribute('aria-label', label);
      button.title = label;
      if (desktop.matches && sidebar) {
        const edge = expanded ? Math.max(0, sidebar.getBoundingClientRect().right - 14) : 0;
        button.style.setProperty('--sidebar-edge', `${edge}px`);
      }
    });
  };

  document.addEventListener('click', (event) => {
    if (!event.target.closest('[data-sidebar-toggle]')) return;
    if (desktop.matches) {
      const hidden = root.classList.toggle('sidebar-hidden');
      try {
        localStorage.setItem('notes:sidebar-hidden', String(hidden));
      } catch {
        // The toggle still works when browser storage is unavailable.
      }
    } else {
      const drawer = document.querySelector('#__drawer');
      if (drawer) {
        drawer.checked = !drawer.checked;
        drawer.dispatchEvent(new Event('change', { bubbles: true }));
      }
    }
    update();
  });
  document.addEventListener('change', (event) => {
    if (event.target.id === '__drawer') update();
  });
  desktop.addEventListener('change', update);
  window.addEventListener('resize', update);
  if (typeof document$ !== 'undefined') document$.subscribe(update);
  else update();
})();
