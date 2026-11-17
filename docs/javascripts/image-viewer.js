(() => {
  const dialog = document.createElement('dialog');
  dialog.className = 'image-viewer';
  dialog.setAttribute('aria-labelledby', 'image-viewer-title');
  dialog.setAttribute('aria-describedby', 'image-viewer-caption image-viewer-help');
  dialog.innerHTML = `
    <div class="image-viewer__toolbar">
      <h2 id="image-viewer-title">Image viewer</h2>
      <div class="image-viewer__controls" role="group" aria-label="Image controls">
        <button type="button" data-action="out" aria-label="Zoom out" title="Zoom out (−)">−</button>
        <output aria-live="polite" aria-label="Zoom level">100%</output>
        <button type="button" data-action="in" aria-label="Zoom in" title="Zoom in (+)">+</button>
        <button type="button" data-action="fit" title="Fit to screen (0)">Fit</button>
        <button type="button" data-action="close" aria-label="Close image viewer" title="Close (Escape)">×</button>
      </div>
    </div>
    <div class="image-viewer__viewport" tabindex="0" aria-label="Image. Scroll or drag to explore when zoomed.">
      <div class="image-viewer__canvas"><img class="image-viewer__image" alt="" draggable="false"></div>
    </div>
    <p id="image-viewer-caption" class="image-viewer__caption"></p>
    <p id="image-viewer-help" class="image-viewer__help">Scroll to zoom · Drag or swipe to pan · Esc to close</p>
  `;
  document.body.append(dialog);

  const viewport = dialog.querySelector('.image-viewer__viewport');
  const image = dialog.querySelector('img');
  const caption = dialog.querySelector('#image-viewer-caption');
  const output = dialog.querySelector('output');
  const zoomIn = dialog.querySelector('[data-action="in"]');
  const zoomOut = dialog.querySelector('[data-action="out"]');
  let opener;
  let scale = 1;
  let fitWidth = 0;
  let fitHeight = 0;
  let drag;

  const render = () => {
    image.style.width = `${fitWidth * scale}px`;
    image.style.height = `${fitHeight * scale}px`;
    output.value = `${Math.round(scale * 100)}%`;
    zoomIn.disabled = scale >= 6;
    zoomOut.disabled = scale <= 0.25;
  };

  const fit = () => {
    if (!dialog.open || !image.naturalWidth) return;
    const ratio = Math.min(1,
      Math.max(1, viewport.clientWidth - 48) / image.naturalWidth,
      Math.max(1, viewport.clientHeight - 48) / image.naturalHeight);
    fitWidth = image.naturalWidth * ratio;
    fitHeight = image.naturalHeight * ratio;
    scale = 1;
    render();
    viewport.scrollTo(0, 0);
  };

  const zoom = (next, clientX, clientY) => {
    if (!fitWidth) return;
    const view = viewport.getBoundingClientRect();
    const before = image.getBoundingClientRect();
    const x = (clientX ?? view.left + viewport.clientWidth / 2) - view.left;
    const y = (clientY ?? view.top + viewport.clientHeight / 2) - view.top;
    const imageX = (x - (before.left - view.left)) / before.width;
    const imageY = (y - (before.top - view.top)) / before.height;
    scale = Math.min(6, Math.max(0.25, next));
    render();
    const after = image.getBoundingClientRect();
    viewport.scrollLeft += after.left - view.left + imageX * after.width - x;
    viewport.scrollTop += after.top - view.top + imageY * after.height - y;
  };

  const open = (source, button) => {
    opener = button;
    fitWidth = 0;
    image.alt = source.alt;
    caption.textContent = source.alt || 'Lesson illustration';
    image.src = source.currentSrc || source.src;
    document.documentElement.classList.add('image-viewer-open');
    dialog.showModal();
    fit();
  };

  image.addEventListener('load', fit);
  dialog.querySelector('[data-action="close"]').addEventListener('click', () => dialog.close());
  dialog.querySelector('[data-action="fit"]').addEventListener('click', fit);
  zoomIn.addEventListener('click', () => zoom(scale * 1.25));
  zoomOut.addEventListener('click', () => zoom(scale / 1.25));
  dialog.addEventListener('close', () => {
    document.documentElement.classList.remove('image-viewer-open');
    drag = undefined;
    viewport.classList.remove('image-viewer__viewport--dragging');
    if (opener?.isConnected) opener.focus({ preventScroll: true });
  });
  dialog.addEventListener('click', (event) => {
    if (event.target !== dialog) return;
    const rect = dialog.getBoundingClientRect();
    if (event.clientX < rect.left || event.clientX > rect.right
        || event.clientY < rect.top || event.clientY > rect.bottom) dialog.close();
  });
  dialog.addEventListener('keydown', (event) => {
    if (event.ctrlKey || event.metaKey || event.altKey) return;
    if (['+', '=', '-', '0'].includes(event.key)) {
      event.preventDefault();
      if (event.key === '0') fit();
      else zoom(event.key === '-' ? scale / 1.25 : scale * 1.25);
    }
  });
  viewport.addEventListener('wheel', (event) => {
    event.preventDefault();
    const delta = event.deltaY * (event.deltaMode === 1 ? 16 : event.deltaMode === 2 ? viewport.clientHeight : 1);
    zoom(scale * Math.exp(-delta * 0.002), event.clientX, event.clientY);
  }, { passive: false });
  viewport.addEventListener('pointerdown', (event) => {
    // Touch scrolling stays native, including momentum and two-axis panning.
    if (event.pointerType !== 'mouse' || event.button !== 0) return;
    drag = { x: event.clientX, y: event.clientY, left: viewport.scrollLeft, top: viewport.scrollTop };
    viewport.setPointerCapture(event.pointerId);
    viewport.classList.add('image-viewer__viewport--dragging');
    event.preventDefault();
  });
  viewport.addEventListener('pointermove', (event) => {
    if (!drag) return;
    viewport.scrollLeft = drag.left + drag.x - event.clientX;
    viewport.scrollTop = drag.top + drag.y - event.clientY;
  });
  const stopDragging = () => {
    drag = undefined;
    viewport.classList.remove('image-viewer__viewport--dragging');
  };
  viewport.addEventListener('pointerup', stopDragging);
  viewport.addEventListener('pointercancel', stopDragging);
  viewport.addEventListener('lostpointercapture', stopDragging);
  window.addEventListener('resize', fit);

  const enhanceImages = () => {
    if (dialog.open) dialog.close();
    document.querySelectorAll('.md-content img:not(.twemoji):not(.emojione)').forEach((source) => {
      if (source.closest('a, button')) return;
      const button = document.createElement('button');
      button.type = 'button';
      button.className = 'image-viewer-trigger';
      button.setAttribute('aria-haspopup', 'dialog');
      button.setAttribute('aria-label', `Open image: ${source.alt || 'Lesson illustration'}`);
      button.title = 'Click to enlarge';
      source.replaceWith(button);
      button.append(source);
      button.addEventListener('click', () => open(source, button));
    });
  };

  if (typeof document$ !== 'undefined') document$.subscribe(enhanceImages);
  else enhanceImages();
})();
