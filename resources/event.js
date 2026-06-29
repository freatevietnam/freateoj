function WSEventDispatcher(socket_url, polling_base, last_msg) {
    socket_url = window.location.protocol + '//' + window.location.host;
    this.socket_url = socket_url;
    this.polling_path = polling_base;
    this.connected = false;
    this.last_msg = last_msg;
    this.events = {};
    this.channels = [];

    var receiver = this;
    var disconnect_secret = 'disconnect_ZQ4hNB3vUc33q7Y7K1os';
    var reconnect_secret = 'reconnect_ZQ4hNB3vUc33q7Y7K1os';
    var socket = null;

    function Event() {
        this.callbacks = [];

        this.registerCallback = function (callback) {
            this.callbacks.push(callback);
        };

        this.fire = function (data) {
            this.callbacks.forEach(function (callback) {
                callback(data);
            });
        };
    }

    function doSubscribe() {
        if (socket && socket.connected && receiver.channels.length > 0) {
            socket.emit('subscribe', {
                channels: receiver.channels,
                last_msg: receiver.last_msg,
            });
        }
    }

    function init_socketio() {
        socket = io(socket_url, {
            transports: ['polling', 'websocket'],
            reconnection: true,
            reconnectionDelay: 1000,
            reconnectionAttempts: Infinity,
        });

        socket.on('connect', function () {
            receiver.connected = true;
            doSubscribe();
        });

        socket.on('event', function (data) {
            receiver.dispatch(data.channel, data.message);
            receiver.last_msg = data.id;
        });

        socket.on('disconnect', function (reason) {
            receiver.connected = false;
            receiver.dispatch(disconnect_secret, {reason: reason});
        });

        socket.on('reconnect', function () {
            receiver.connected = true;
            receiver.dispatch(reconnect_secret, {});
        });
    }

    function init_poll() {
        function long_poll() {
            receiver.polling_request = $.ajax({
                url: receiver.polling_path,
                data: { last: receiver.last_msg },
                success: function (data) {
                    receiver.dispatch(data.channel, data.message);
                    receiver.last_msg = data.id;
                    long_poll();
                },
                error: function (jqXHR, status) {
                    if (jqXHR.status == 504) {
                        long_poll();
                    } else if (status !== 'abort') {
                        console.log('Long poll failure: ' + status);
                        setTimeout(long_poll, 2000);
                    }
                },
                dataType: 'json',
            });
        }
        long_poll();
    }

    function init_connection() {
        if (typeof io !== 'undefined') {
            init_socketio();
        } else {
            init_poll();
        }
    }

    this.dispatch = function (event_name, data) {
        var event = this.events[event_name];
        if (event) {
            event.fire(data);
        }
    };

    this.on = function (event_name, callback) {
        if (!this.connected && !socket) {
            init_connection();
        }
        if (!this.events[event_name]) {
            this.events[event_name] = new Event();
            this.channels.push(event_name);

            doSubscribe();
        }
        this.events[event_name].registerCallback(callback);
    };

    this.ondisconnect = function (callback) {
        if (!this.events[disconnect_secret]) {
            this.events[disconnect_secret] = new Event();
        }
        this.events[disconnect_secret].registerCallback(callback);
    };

    this.onreconnect = function (callback) {
        if (!this.events[reconnect_secret]) {
            this.events[reconnect_secret] = new Event();
        }
        this.events[reconnect_secret].registerCallback(callback);
    };
}
