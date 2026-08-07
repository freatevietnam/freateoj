/* Contest Replay & Ghost Participation Handling */

(function () {
    'use strict';

    function blockForVirtual($el, tooltip) {
        $el.addClass('replay-blocked').attr('data-tooltip', tooltip);
        $el.children().css({ 'opacity': 0.5, 'pointer-events': 'none' });
        $el.find('input, button').prop('disabled', true);
    }

    $(function () {
        var showVirtual = window.CONTEST_SHOW_VIRTUAL;
        var virtualTooltip = window.CONTEST_REPLAY_VIRTUAL_TOOLTIP;

        if (showVirtual) {
            var $tip = null;
            $(document)
                .on('mouseenter', '.replay-blocked', function () {
                    if (!$tip) $tip = $('<div class="replay-tooltip"></div>').appendTo('body');
                    $tip.text($(this).attr('data-tooltip')).show();
                })
                .on('mousemove', '.replay-blocked', function (e) {
                    if ($tip) $tip.css({ left: (e.clientX + 12) + 'px', top: (e.clientY + 12) + 'px' });
                })
                .on('mouseleave', '.replay-blocked', function () {
                    if ($tip) $tip.hide();
                });
        }

        var $ghost = $('#show-ghosts-checkbox');
        if ($ghost.length && showVirtual) {
            blockForVirtual($('#show-ghosts-wrap'), virtualTooltip);
        }
    });

    window.ContestReplay = {
        container: null,
        data: null,
        playing: false,
        speed: 1,
        currentTime: 0,
        timeline: null,

        init: function (container, url) {
            this.container = container;
            this.url = url;
            this.renderControls();
            this.loadReplayData(url);
        },

        loadReplayData: function (url) {
            var self = this;
            fetch(url)
                .then(function (response) { return response.json(); })
                .then(function (data) {
                    self.data = data;
                    self.render();
                })
                .catch(function (err) {
                    console.error('Failed to load replay data:', err);
                });
        },

        renderControls: function () {
            if (!this.container) return;
            var html = '<div class="replay-controls">' +
                '<button id="replay-play">Play</button>' +
                '<button id="replay-pause" disabled>Pause</button>' +
                '<button id="replay-reset">Reset</button>' +
                '<select id="replay-speed">' +
                '<option value="0.5">0.5x</option>' +
                '<option value="1" selected>1x</option>' +
                '<option value="2">2x</option>' +
                '<option value="4">4x</option>' +
                '</select>' +
                '<input type="range" id="replay-timeline" min="0" max="100" value="0" style="width: 200px;">' +
                '</div>' +
                '<div id="replay-ranking"></div>';
            this.container.innerHTML = html;
        },

        render: function () {
            if (!this.data || !this.container) return;
            var rankingDiv = this.container.querySelector('#replay-ranking');
            if (rankingDiv) {
                rankingDiv.innerHTML = '<p>Replay data loaded. Player not yet implemented.</p>';
            }
        },

        play: function () {
            this.playing = true;
        },

        pause: function () {
            this.playing = false;
        },

        reset: function () {
            this.currentTime = 0;
            this.playing = false;
        },

        setSpeed: function (speed) {
            this.speed = speed;
        }
    };
})();
