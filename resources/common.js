window.isMobile = function () {
    return window.matchMedia('(max-width: 760px)').matches;
};

if (!String.prototype.startsWith) {
    String.prototype.startsWith = function (searchString, position) {
        return this.substr(position || 0, searchString.length) === searchString;
    };
}

if (!String.prototype.endsWith) {
    String.prototype.endsWith = function (searchString, position) {
        var subjectString = this.toString();
        if (typeof position !== 'number' || !isFinite(position) || Math.floor(position) !== position || position > subjectString.length) {
            position = subjectString.length;
        }
        position -= searchString.length;
        var lastIndex = subjectString.lastIndexOf(searchString, position);
        return lastIndex !== -1 && lastIndex === position;
    };
}

// https://stackoverflow.com/a/1060034/1090657
$(function () {
    var hidden = 'hidden';

    // Standards:
    if (hidden in document)
        document.addEventListener('visibilitychange', onchange);
    else if ((hidden = 'mozHidden') in document)
        document.addEventListener('mozvisibilitychange', onchange);
    else if ((hidden = 'webkitHidden') in document)
        document.addEventListener('webkitvisibilitychange', onchange);
    else if ((hidden = 'msHidden') in document)
        document.addEventListener('msvisibilitychange', onchange);
    // IE 9 and lower:
    else if ('onfocusin' in document)
        document.onfocusin = document.onfocusout = onchange;
    // All others:
    else
        window.onpageshow = window.onpagehide
            = window.onfocus = window.onblur = onchange;

    function onchange(evt) {
        var v = 'window-visible', h = 'window-hidden', evtMap = {
            focus: v, focusin: v, pageshow: v, blur: h, focusout: h, pagehide: h
        };

        evt = evt || window.event;
        if (evt.type in evtMap)
            document.body.className = evtMap[evt.type];
        else
            document.body.className = this[hidden] ? 'window-hidden' : 'window-visible';

        if ('$' in window)
            $(window).trigger('dmoj:' + document.body.className);
    }

    // set the initial state (but only if browser supports the Page Visibility API)
    if (document[hidden] !== undefined)
        onchange({type: document[hidden] ? 'blur' : 'focus'});
});

function register_toggle(link) {
    link.click(function () {
        var toggled = link.next('.toggled');
        if (toggled.is(':visible')) {
            toggled.hide(400);
            link.removeClass('open');
            link.addClass('closed');
        } else {
            toggled.show(400);
            link.addClass('open');
            link.removeClass('closed');
        }
    });
}

$(function register_all_toggles() {
    $('.toggle').each(function () {
        register_toggle($(this));
    });
});

function featureTest(property, value, noPrefixes) {
    var prop = property + ':',
        el = document.createElement('test'),
        mStyle = el.style;

    if (!noPrefixes) {
        mStyle.cssText = prop + ['-webkit-', '-moz-', '-ms-', '-o-', ''].join(value + ';' + prop) + value + ';';
    } else {
        mStyle.cssText = prop + value;
    }
    return !!mStyle[property];
}

window.fix_div = function (div, height) {
    var div_offset = div.offset().top - $('html').offset().top;
    var is_moving;
    var moving = function () {
        div.css('position', 'absolute').css('top', div_offset);
        is_moving = true;
    };
    var fix = function () {
        div.css('position', 'fixed').css('top', height);
        is_moving = false;
    };
    ($(window).scrollTop() - div_offset > -height) ? fix() : moving();
    $(window).scroll(function () {
        if (($(window).scrollTop() - div_offset > -height) == is_moving)
            is_moving ? fix() : moving();
    });
};

$(function () {
    if (typeof window.orientation !== 'undefined') {
        $(window).resize(function () {
            var width = Math.max(document.documentElement.clientWidth, window.innerWidth || 0);
            $('#viewport').attr('content', width > 480 ? 'initial-scale=1' : 'width=480');
        });
    }

    var $nav_list = $('#nav-list');
    var $navicon = $('#navicon');
    var $user_links = $('#user-links');
    var $body = $('body');

    function closeMobileMenu() {
        if ($nav_list && $nav_list.length) $nav_list.removeClass('show-list');
        if ($navicon && $navicon.length) $navicon.removeClass('active');
        if ($body && $body.length) $body.removeClass('mobile-menu-open');
    }

    $navicon.click(function (event) {
        event.stopPropagation();
        $nav_list.toggleClass('show-list');
        $navicon.toggleClass('active');
        $body.toggleClass('mobile-menu-open');
        if (!$nav_list.hasClass('show-list'))
            $(this).blur().removeClass('hover');
        else {
            $(this).addClass('hover');
        }
    }).hover(function () {
        $(this).addClass('hover');
    }, function () {
        $(this).removeClass('hover');
    });

    // Auto-scale nav font-size để vừa khít navbar
    var NAV_SCALE_STORAGE_KEY = 'nav-scale-factor';

    function autoScaleNav() {
        var nav = document.getElementById('navigation');
        var container = document.getElementById('nav-container');
        if (!nav || !container) return;

        var navList = document.getElementById('nav-list');
        var userLinks = document.getElementById('user-links');
        if (!navList || !userLinks) return;

        // ===== RESET: Hiện tất cả các element đã bị ẩn trước đó =====
        var toToggle = [
            navList.querySelectorAll('.home-nav-element'),
            userLinks.querySelectorAll('a > span > span'),         // "Xin chào, ..."
            userLinks.querySelectorAll('.notification-wrapper'),   // chuông
            userLinks.querySelectorAll('a[href*="ticket"]'),       // report issue
            userLinks.querySelectorAll('a[href*="misc_config"], a[href*="settings"]'), // bánh răng (superuser)
            userLinks.querySelectorAll('#user-links > ul:first-child > li'), // settings dropdown
        ];
        toToggle.forEach(function (els) {
            els.forEach(function (el) { el.style.display = ''; });
        });
        userLinks.style.display = '';

        // Thu thập các element cần scale (chỉ scale các span/a của nav-items)
        var navItems = navList.querySelectorAll(':scope > li > a');
        var itemsData = [];
        navItems.forEach(function (a) {
            var span = a.querySelector(':scope > span');
            var computedA = getComputedStyle(a);
            var computedSpan = span ? getComputedStyle(span) : null;
            itemsData.push({
                a: a,
                span: span,
                aFontSize: parseFloat(computedA.fontSize),
                aPaddingTop: parseFloat(computedA.paddingTop),
                aPaddingRight: parseFloat(computedA.paddingRight),
                aPaddingBottom: parseFloat(computedA.paddingBottom),
                aPaddingLeft: parseFloat(computedA.paddingLeft),
                spanFontSize: computedSpan ? parseFloat(computedSpan.fontSize) : 0,
                spanPaddingTop: computedSpan ? parseFloat(computedSpan.paddingTop) : 0,
                spanPaddingRight: computedSpan ? parseFloat(computedSpan.paddingRight) : 0,
                spanPaddingBottom: computedSpan ? parseFloat(computedSpan.paddingBottom) : 0,
                spanPaddingLeft: computedSpan ? parseFloat(computedSpan.paddingLeft) : 0,
            });
        });

        function applyFactor(factor) {
            // factor: 1.0 = gốc, 0.5 = một nửa
            itemsData.forEach(function (it) {
                it.a.style.fontSize = (it.aFontSize * factor) + 'px';
                it.a.style.padding = (it.aPaddingTop * factor) + 'px '
                    + (it.aPaddingRight * factor) + 'px '
                    + (it.aPaddingBottom * factor) + 'px '
                    + (it.aPaddingLeft * factor) + 'px';
                if (it.span) {
                    it.span.style.fontSize = (it.spanFontSize * factor) + 'px';
                    it.span.style.padding = (it.spanPaddingTop * factor) + 'px '
                        + (it.spanPaddingRight * factor) + 'px '
                        + (it.spanPaddingBottom * factor) + 'px '
                        + (it.spanPaddingLeft * factor) + 'px';
                }
            });
        }

        function hideElements(els) {
            els.forEach(function (el) { el.style.display = 'none'; });
        }

        function measure() {
            return {
                nav: nav.clientWidth,
                list: navList.scrollWidth,
                user: userLinks.offsetWidth,
                total: navList.scrollWidth + userLinks.offsetWidth
            };
        }

        applyFactor(1);

        requestAnimationFrame(function () {
            requestAnimationFrame(function () {
                var navWidth = nav.clientWidth;

                // Bước 1: ẨN dần các element ít quan trọng
                var m = measure();
                if (m.total > navWidth) {
                    hideElements(navList.querySelectorAll('.home-nav-element'));
                    m = measure();
                }
                if (m.total > navWidth) {
                    hideElements(userLinks.querySelectorAll('#user-links > ul:first-child > li'));
                    hideElements(userLinks.querySelectorAll('a[href*="misc_config"]'));
                    m = measure();
                }
                if (m.total > navWidth) {
                    hideElements(userLinks.querySelectorAll('a[href*="ticket"]'));
                    m = measure();
                }
                if (m.total > navWidth) {
                    hideElements(userLinks.querySelectorAll('.notification-wrapper'));
                    m = measure();
                }
                if (m.total > navWidth) {
                    hideElements(userLinks.querySelectorAll('a > span > span'));
                    m = measure();
                }
                if (m.total > navWidth) {
                    userLinks.style.display = 'none';
                    m = measure();
                }

                // Bước 2: Scale giảm dần cho đến khi vừa khít (không giới hạn số lần)
                // Bắt đầu từ factor trong cache nếu có
                var cachedFactor = null;
                try {
                    var raw = localStorage.getItem(NAV_SCALE_STORAGE_KEY);
                    if (raw) cachedFactor = parseFloat(raw);
                } catch (e) { /* ignore */ }

                var factor = (cachedFactor && cachedFactor > 0.4 && cachedFactor <= 1) ? cachedFactor : 1;
                applyFactor(factor);

                // Đo lại sau khi apply cached
                requestAnimationFrame(function () {
                    m = measure();
                    var minFactor = 0.4;
                    var maxFactor = 1;

                    // Nếu vẫn tràn: giảm dần đến khi vừa khít
                    if (m.total > navWidth) {
                        var step = 0.02;
                        while (factor > minFactor) {
                            factor -= step;
                            applyFactor(factor);
                            m = measure();
                            if (m.total <= navWidth) break;
                            if (factor <= minFactor) break;
                        }
                    } else {
                        // Nếu dư nhiều: tăng dần đến khi vừa khít
                        var stepUp = 0.02;
                        while (factor < maxFactor) {
                            var testFactor = factor + stepUp;
                            applyFactor(testFactor);
                            m = measure();
                            if (m.total > navWidth) {
                                applyFactor(factor);
                                m = measure();
                                break;
                            }
                            factor = testFactor;
                        }
                    }

                    // Lưu vào localStorage
                    try {
                        localStorage.setItem(NAV_SCALE_STORAGE_KEY, factor.toString());
                    } catch (e) { /* ignore */ }
                });
            });
        });
    }

    // Chạy sau khi DOM sẵn sàng và sau khi load font
    var scaleRan = false;
    function runScale(forceReset) {
        if (forceReset) {
            scaleRan = false;
            try { localStorage.removeItem(NAV_SCALE_STORAGE_KEY); } catch (e) {}
        }
        if (scaleRan) return;
        scaleRan = true;
        autoScaleNav();
    }

    $(window).on('load', function () {
        runScale();
    });
    $(document).ready(function () {
        // Chạy nhiều lần trong vài giây đầu vì font có thể load chậm
        runScale();
        setTimeout(function () { runScale(); }, 200);
        setTimeout(function () { runScale(); }, 500);
        setTimeout(function () { runScale(); }, 1000);
    });

    // ResizeObserver: chỉ reset cache khi width thay đổi đáng kể (>20%)
    var lastNavWidth = 0;
    if (window.ResizeObserver) {
        var ro = new ResizeObserver(function (entries) {
            for (var i = 0; i < entries.length; i++) {
                var w = entries[i].contentRect.width;
                if (lastNavWidth && (Math.abs(w - lastNavWidth) / lastNavWidth) > 0.2) {
                    runScale(true); // reset cache
                } else {
                    runScale(false); // dùng cache
                }
                lastNavWidth = w;
                break;
            }
        });
        var nav = document.getElementById('navigation');
        if (nav) ro.observe(nav);
    } else {
        $(window).on('resize', function () {
            runScale(true);
        });
    }

    // Đóng mobile menu khi resize sang desktop
    $(window).on('resize', function () {
        if (!window.isMobile() && $body.hasClass('mobile-menu-open')) {
            closeMobileMenu();
        }
    });

    $nav_list.find('li a .nav-expand').click(function (event) {
        event.preventDefault();
        $(this).parent().siblings('ul').toggleClass('show-list');
    });

    $nav_list.find('li a').each(function () {
        if (!$(this).siblings('ul').length)
            return;
        $(this).on('contextmenu', function (event) {
            event.preventDefault();
        }).on('taphold', function () {
            $(this).siblings('ul').css('display', 'block');
        });
    });

    $nav_list.click(function (event) {
        event.stopPropagation();
    });

    $('html').click(function () {
        closeMobileMenu();
    });

    // Sliding underline for navbar
    var $navUl = $('#nav-list > li').parent();
    var $underline = $('<div class="nav-underline"></div>').appendTo($navUl);

    function updateUnderline($link) {
        if (!$link || !$link.length) return;
        // Disable animation khi scale quá nhỏ (font-size dưới ngưỡng đọc được)
        var cachedFactor = 1;
        try {
            var raw = localStorage.getItem(NAV_SCALE_STORAGE_KEY);
            if (raw) cachedFactor = parseFloat(raw);
        } catch (e) { /* ignore */ }
        if (cachedFactor < 0.7) return;

        var navOffset = $navUl.offset();
        var linkOffset = $link.offset();
        if (!navOffset || !linkOffset) return;

        var navLeft = navOffset.left;
        var linkLeft = linkOffset.left;
        var width = $link.outerWidth();

        $underline.css({
            left: (linkLeft - navLeft) + 'px',
            width: width + 'px',
            opacity: 1
        });
    }

    $('#nav-list > li').on('mouseenter', function() {
        var $item = $(this);
        var $link = $item.children('a, button').first();
        updateUnderline($link);
    }).on('mouseleave', function() {
        $underline.css('opacity', 0);
    });

    // Set initial underline position to active item
    var $activeItem = $('#nav-list > li').has('.active');
    function setInitialUnderline() {
        var cachedFactor = 1;
        try {
            var raw = localStorage.getItem(NAV_SCALE_STORAGE_KEY);
            if (raw) cachedFactor = parseFloat(raw);
        } catch (e) { /* ignore */ }
        if (cachedFactor < 0.7) {
            $underline.css('opacity', 0);
            return;
        }
        if ($activeItem.length) {
            var $link = $activeItem.children('a, button').first();
            updateUnderline($link);
        }
    }

    // Wait for fonts to load before setting initial position
    if (document.fonts && document.fonts.ready) {
        document.fonts.ready.then(setInitialUnderline);
    } else {
        setInitialUnderline();
    }

    // Update underline on resize
    $(window).on('resize', function() {
        var $hoveredItem = $('#nav-list > li:hover');
        if ($hoveredItem.length) {
            $hoveredItem.trigger('mouseenter');
        } else if ($activeItem.length) {
            var $link = $activeItem.children('a, button').first();
            updateUnderline($link);
        }
    });

    $.ajaxSetup({
        beforeSend: function (xhr, settings) {
            if (!(/^(GET|HEAD|OPTIONS|TRACE)$/.test(settings.type)) && !this.crossDomain)
                xhr.setRequestHeader('X-CSRFToken', $.cookie('csrftoken'));
        }
    });
});

if (!Date.now) {
    Date.now = function () {
        return new Date().getTime();
    };
}

function count_down(label) {
    var initial = parseInt(label.attr('data-secs'));
    var start = Date.now();

    function format(num) {
        var s = "0" + num;
        return s.substr(s.length - 2);
    }

    var timer = setInterval(function () {
        var time = Math.round(initial - (Date.now() - start) / 1000);
        if (time <= 0) {
            clearInterval(timer);
            setTimeout(function() {
                window.location.reload();
            }, 2000);
        }
        var d = Math.floor(time / 86400);
        var h = Math.floor(time % 86400 / 3600);
        var m = Math.floor(time % 3600 / 60);
        var s = time % 60;
        if (d > 0)
            label.text(npgettext('time format with day', '%d day %h:%m:%s', '%d days %h:%m:%s', d)
                .replace('%d', d).replace('%h', format(h)).replace('%m', format(m)).replace('%s', format(s)));
        else
            label.text(pgettext('time format without day', '%h:%m:%s')
                .replace('%h', format(h)).replace('%m', format(m)).replace('%s', format(s)));
    }, 1000);
}

function register_time(elems, limit) {
    if (typeof moment === 'undefined') return;
    limit = 60;
    elems.each(function () {
        var outdated = false;
        var $this = $(this);
        var time = moment($this.attr('data-iso'));
        var rel_format = $this.attr('data-format');

        function update() {
            if ($('body').hasClass('window-hidden'))
                return outdated = true;
            outdated = false;
            if (moment().diff(time, 'seconds') < limit) {
                $this.text(rel_format.replace('{time}', time.fromNow()));
            } else {
                $this.text(rel_format.replace('{time}', time.format("h:mm:ss a, DD/MM/YYYY")));
            }
            setTimeout(update, 10000);
        }

        $(window).on('dmoj:window-visible', function () {
            if (outdated)
                update();
        });

        update();
    });
}

$(function () {
    register_time($('.time-with-rel'));

    $('form').submit(function (evt) {
        // Prevent multiple submissions of forms, see #565
        $("button[type=submit], input[type=submit]").prop('disabled', true);
    });
});

window.notification_template = {
    icon: '/static/icons/logo.png'
};
window.notification_timeout = 5000;

window.notify = function (type, title, data, timeout) {
    if (localStorage[type + '_notification'] != 'true') return;
    var template = window[type + '_notification_template'] || window.notification_template;
    var data = (typeof data !== 'undefined' ? $.extend({}, template, data) : template);
    var object = new Notification(title, data);
    if (typeof timeout === 'undefined')
        timeout = window.notification_timeout;
    if (timeout)
        setTimeout(function () {
            object.close();
        }, timeout);
    return object;
};

window.register_notify = function (type, options) {
    if (typeof options === 'undefined')
        options = {};

    function status_change() {
        if ('change' in options)
            options.change(localStorage[key] == 'true');
    }

    var key = type + '_notification';
    if ('Notification' in window) {
        if (!(key in localStorage) || Notification.permission !== 'granted')
            localStorage[key] = 'false';

        if ('$checkbox' in options) {
            options.$checkbox.change(function () {
                var status = $(this).is(':checked');
                if (status) {
                    if (Notification.permission === 'granted') {
                        localStorage[key] = 'true';
                        notify(type, 'Notification enabled!');
                        status_change();
                    } else
                        Notification.requestPermission(function (permission) {
                            if (permission === 'granted') {
                                localStorage[key] = 'true';
                                notify(type, 'Notification enabled!');
                            } else localStorage[key] = 'false';
                            status_change();
                        });
                } else {
                    localStorage[key] = 'false';
                    status_change();
                }
            }).prop('checked', localStorage[key] == 'true');
        }

        $(window).on('storage', function (e) {
            e = e.originalEvent;
            if (e.key === key) {
                if ('$checkbox' in options)
                    options.$checkbox.prop('checked', e.newValue == 'true');
                status_change();
            }
        });
    } else {
        if ('$checkbox' in options) options.$checkbox.hide();
        localStorage[key] = 'false';
    }
    status_change();
};


$(function () {
    // Close dismissable boxes
    $("a.close").click(function () {
        var $closer = $(this);
        $closer.parent().fadeOut(200);
    });
});

$(function () {
    // Reveal spoiler
    $(document).on('click', 'blockquote.spoiler', function (e) {
        $(this).addClass("is-visible");
        e.stopPropagation();
    } );
});
