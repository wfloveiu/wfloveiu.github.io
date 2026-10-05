(() => {
  const menu = document.querySelector('.menu-toggle');
  const navigation = document.querySelector('.nav-links');
  if (menu && navigation) {
    document.documentElement.classList.add('js-menu');
    menu.hidden = false;
    const closeMenu = () => { menu.setAttribute('aria-expanded', 'false'); navigation.classList.remove('is-open'); };
    menu.addEventListener('click', () => {
      const expanded = menu.getAttribute('aria-expanded') !== 'true';
      menu.setAttribute('aria-expanded', String(expanded));
      navigation.classList.toggle('is-open', expanded);
    });
    document.addEventListener('keydown', event => { if (event.key === 'Escape' && menu.getAttribute('aria-expanded') === 'true') { closeMenu(); menu.focus(); } });
    navigation.addEventListener('click', event => { if (event.target.closest('a')) closeMenu(); });
  }

  const search = document.querySelector('#post-search');
  if (search) {
    document.querySelector('.blog-controls').hidden = false;
    const entries = [...document.querySelectorAll('[data-post]')].map(element => ({element, text: element.dataset.search.toLocaleLowerCase(), categories: JSON.parse(element.dataset.categories)}));
    const buttons = [...document.querySelectorAll('[data-category]')];
    const status = document.querySelector('#search-status');
    let category = '';
    const update = () => {
      const terms = search.value.trim().toLocaleLowerCase().split(/\s+/).filter(Boolean);
      let count = 0;
      entries.forEach(entry => {
        const categoryMatch = !category || (category === '__uncategorized' ? entry.categories.length === 0 : entry.categories.includes(category));
        const visible = categoryMatch && terms.every(term => entry.text.includes(term));
        entry.element.hidden = !visible;
        if (visible) count++;
      });
      status.textContent = terms.length || category ? `找到 ${count} 篇文章` : '';
      document.querySelector('.empty-state').hidden = count !== 0;
      buttons.forEach(button => button.setAttribute('aria-pressed', String(button.dataset.category === category)));
    };
    search.addEventListener('input', update);
    buttons.forEach(button => button.addEventListener('click', () => { category = button.dataset.category; update(); }));
    document.querySelector('#clear-search').addEventListener('click', () => { search.value = ''; category = ''; update(); search.focus(); });
    document.addEventListener('keydown', event => {
      if (event.key === '/' && !/INPUT|TEXTAREA|SELECT/.test(document.activeElement.tagName) && !document.activeElement.isContentEditable) { event.preventDefault(); search.focus(); }
      if (event.key === 'Escape' && document.activeElement === search) { search.value = ''; update(); }
    });
  }

  const publicationFilters = document.querySelector('.publication-filters');
  if (publicationFilters) {
    publicationFilters.hidden = false;
    const buttons = [...publicationFilters.querySelectorAll('[data-publication-topic]')];
    const publications = [...document.querySelectorAll('[data-publication]')];
    buttons.forEach(button => button.addEventListener('click', () => {
      const topic = button.dataset.publicationTopic;
      buttons.forEach(item => item.setAttribute('aria-pressed', String(item === button)));
      publications.forEach(item => { item.hidden = !!topic && !JSON.parse(item.dataset.topics).includes(topic); });
      document.querySelectorAll('[data-publication-year]').forEach(year => { year.hidden = !year.querySelector('[data-publication]:not([hidden])'); });
    }));
  }

  if (navigator.clipboard && window.isSecureContext) {
    document.querySelectorAll('.post-content pre').forEach(pre => {
      const code = pre.querySelector('code');
      if (!code) return;
      const button = document.createElement('button');
      button.type = 'button'; button.className = 'copy-code'; button.textContent = '复制代码';
      button.addEventListener('click', async () => {
        try { await navigator.clipboard.writeText(code.textContent); button.textContent = '已复制'; }
        catch { button.textContent = '复制失败，请手动选择'; }
        setTimeout(() => { button.textContent = '复制代码'; }, 2000);
      });
      pre.prepend(button);
    });
  }
})();
