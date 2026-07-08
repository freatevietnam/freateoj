window.MathJax = {
    loader: {
        load: ['[tex]/color'],
        paths: {
            mathjax: '/static/freateoj/mathjax/3.2.0/es5'
        }
    },
    tex: {
        packages: {
            '[+]': ['color']
        },
        // FreateOJ uses $ as the default inline math delimiter.
        // Example: $0 \le N \le 10^9$
        // Display math uses $$: $$\sum_{i=1}^{n} i = \frac{n(n+1)}{2}$$
        inlineMath: [
            ['$', '$']
        ],
        displayMath: [
            ['$$', '$$']
        ],
        processEscapes: true
    },
    options: {
        enableMenu: false
    }
};
