jQuery(function ($) {
    var mathJaxReady = false;
    var mathJaxLoading = false;
    var pendingTypesets = [];

    function update_math($content) {
        if (typeof MathJax === 'undefined' || !MathJax.typesetPromise) return;
        try {
            MathJax.typesetPromise([$content[0]]).then(function () {
                $content.find('.tex-image').hide();
                $content.find('.tex-text').show();
            }).catch(function () {});
        } catch (err) {}
    }

    function loadScript(url, callback) {
        var script = document.createElement('script');
        script.src = url;
        script.async = true;
        script.onload = callback;
        script.onerror = function () {};
        document.head.appendChild(script);
    }

    function ensureMathJax(callback) {
        if (mathJaxReady) {
            callback();
            return;
        }
        if ('MathJax' in window && MathJax.startup && MathJax.startup.promise) {
            mathJaxReady = true;
            MathJax.startup.promise.then(callback);
            return;
        }
        if (mathJaxLoading) {
            pendingTypesets.push(callback);
            return;
        }
        mathJaxLoading = true;

        var configUrl = '/static/mathjax_config.js';
        var mathjaxUrl = '/static/freateoj/mathjax/3.2.0/es5/tex-chtml.min.js';

        if (!('MathJax' in window)) {
            loadScript(configUrl, function () {
                loadScript(mathjaxUrl, function () {
                    mathJaxReady = true;
                    var cb = callback;
                    pendingTypesets.forEach(function (fn) { fn(); });
                    pendingTypesets = [];
                    if (MathJax.startup && MathJax.startup.promise) {
                        MathJax.startup.promise.then(cb);
                    } else {
                        cb();
                    }
                });
            });
        } else {
            loadScript(mathjaxUrl, function () {
                mathJaxReady = true;
                var cb = callback;
                pendingTypesets.forEach(function (fn) { fn(); });
                pendingTypesets = [];
                if (MathJax.startup && MathJax.startup.promise) {
                    MathJax.startup.promise.then(cb);
                } else {
                    cb();
                }
            });
        }
    }

    $(document).on('martor:preview', function (e, $content) {
        var $jax = $content.find('.require-mathjax-support');
        if ($jax.length) {
            ensureMathJax(function () {
                update_math($content);
            });
        }
    });
});
