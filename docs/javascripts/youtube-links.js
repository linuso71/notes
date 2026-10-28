document$.subscribe(() => {
  document.querySelectorAll('.md-content a[href]').forEach((link) => {
    const url = new URL(link.href);
    const isYouTube = url.hostname === 'youtu.be'
      || url.hostname === 'youtube.com'
      || url.hostname.endsWith('.youtube.com');
    const hasTimestamp = url.searchParams.has('t')
      || url.searchParams.has('start')
      || url.searchParams.has('time_continue')
      || url.hash.startsWith('#t=');

    if (isYouTube && hasTimestamp) {
      link.target = '_blank';
      link.relList.add('noopener', 'noreferrer');
    }
  });
});
