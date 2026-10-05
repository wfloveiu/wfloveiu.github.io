(() => {
  const article = document.querySelector('#article-container');
  if (!article || typeof renderMathInElement !== 'function') return;
  renderMathInElement(article, {
    delimiters: [
      {left: '$$', right: '$$', display: true},
      {left: '$', right: '$', display: false},
      {left: '\\(', right: '\\)', display: false},
      {left: '\\[', right: '\\]', display: true},
    ],
    throwOnError: false,
    trust: false,
  });
})();
